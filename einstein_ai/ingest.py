import os
import requests
import hashlib
from urllib.parse import urlparse
from dotenv import load_dotenv
from langchain_community.document_loaders import (
    DirectoryLoader,
    TextLoader,
    PyPDFLoader,
    WebBaseLoader
)
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from einstein_ai.utils import logger, get_history_dir

# Load HF_TOKEN and potentially source URLs from environment file
load_dotenv("HF_TOKEN.env")

# Set USER_AGENT to avoid warning from WebBaseLoader
os.environ["USER_AGENT"] = "EinsteinAI/1.0 (Retriever Bot)"

def get_online_sources():
    """Parses SOURCES.env for Einstein source URLs and triggers"""
    sources = []
    if os.path.exists("SOURCES.env"):
        with open("SOURCES.env", "r") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    try:
                        # Format: NAME=URL|T1,T2
                        parts = line.split("=", 1)
                        if len(parts) == 2:
                            val_parts = parts[1].split("|")
                            url = val_parts[0]
                            triggers = val_parts[1].split(",") if len(val_parts) > 1 else []
                            sources.append({"name": parts[0], "url": url, "triggers": triggers})
                    except Exception as e:
                        logger.error(f"Error parsing line in SOURCES.env: {line}. {e}")
    return sources

def cache_web_content(url, name=None):
    """Downloads content from URL and caches it locally, preserving original filename if possible"""
    cache_dir = os.path.join("einstein_ai", "data", "cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    parsed_url = urlparse(url)
    url_filename = os.path.basename(parsed_url.path)

    if not url_filename or url_filename in ['', '/']:
        if name:
            url_filename = name
        else:
            url_filename = "source_" + hashlib.md5(url.encode()).hexdigest()[:8]

    if url.lower().endswith(".pdf") and not url_filename.lower().endswith(".pdf"):
        url_filename += ".pdf"
    elif not any(url_filename.lower().endswith(ext) for ext in [".txt", ".pdf", ".html", ".htm"]):
        url_filename += ".txt"

    safe_name = "".join([c for c in url_filename if c.isalnum() or c in (' ', '.', '_', '-')]).rstrip()
    cache_path = os.path.join(cache_dir, safe_name)

    if os.path.exists(cache_path):
        logger.info(f"Using cached version of {url_filename} from {cache_path}")
        return cache_path

    logger.info(f"Caching {url} to {cache_path}...")
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        with open(cache_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return cache_path
    except Exception as e:
        logger.error(f"Failed to cache {url}: {e}")
        return None

def ingest_docs(custom_source=None):
    data_path = "einstein_ai/data/"
    history_path = get_history_dir()
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    # 1. Handle web sources or custom imports (Download and Cache)
    if custom_source:
        if custom_source.startswith("http"):
            logger.info(f"Processing URL: {custom_source}")
            cache_web_content(custom_source)
        elif os.path.exists(custom_source):
            import shutil
            dest = os.path.join(data_path, os.path.basename(custom_source))
            if os.path.abspath(custom_source) != os.path.abspath(dest):
                shutil.copy2(custom_source, dest)
                logger.info(f"Copied {custom_source} to {dest}")

    # 2. Populate cache from SOURCES.env
    online_sources = get_online_sources()
    if online_sources:
        for source in online_sources:
            cache_web_content(source['url'], source['name'])

    # 3. Load all documents recursively from data_path AND history_path
    logger.info(f"Loading documents from {data_path} and {history_path}...")
    documents = []

    # Text files - Recursive
    for path in [data_path, history_path]:
        txt_loader = DirectoryLoader(
            path,
            glob="**/*.txt",
            loader_cls=TextLoader,
            loader_kwargs={"encoding": "utf-8"},
            recursive=True
        )
        documents.extend(txt_loader.load())

        pdf_loader = DirectoryLoader(
            path,
            glob="**/*.pdf",
            loader_cls=PyPDFLoader,
            recursive=True
        )
        documents.extend(pdf_loader.load())

    if not documents:
        logger.warning("No documents found to index.")
        return

    # Use smaller chunk size to stay within context limits
    logger.info(f"Splitting {len(documents)} documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=600, chunk_overlap=120)
    texts = text_splitter.split_documents(documents)

    logger.info("Initializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    logger.info("Building FAISS index (Memory Update)...")
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("einstein_ai/faiss_index")
    logger.info(f"Successfully created FAISS index with {len(texts)} chunks.")

if __name__ == "__main__":
    import sys
    source = sys.argv[1] if len(sys.argv) > 1 else None
    ingest_docs(source)
