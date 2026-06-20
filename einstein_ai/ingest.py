import os
import requests
import hashlib
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
from einstein_ai.utils import logger

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
                if line.strip() and not line.startswith("#"):
                    try:
                        # Format: NAME=URL|T1,T2
                        parts = line.strip().split("=", 1)
                        if len(parts) == 2:
                            val_parts = parts[1].split("|")
                            url = val_parts[0]
                            triggers = val_parts[1].split(",") if len(val_parts) > 1 else []
                            sources.append({"name": parts[0], "url": url, "triggers": triggers})
                    except Exception as e:
                        logger.error(f"Error parsing line in SOURCES.env: {line}. {e}")
    return sources

def cache_web_content(url, name):
    """Downloads content from URL and caches it locally"""
    cache_dir = os.path.join("einstein_ai", "data", "cache")
    if not os.path.exists(cache_dir):
        os.makedirs(cache_dir)

    # Create a safe filename
    safe_name = "".join([c for c in name if c.isalnum() or c in (' ', '.', '_')]).rstrip()
    cache_path = os.path.join(cache_dir, f"{safe_name}.txt")

    if os.path.exists(cache_path):
        logger.info(f"Using cached version of {name} from {cache_path}")
        return cache_path

    logger.info(f"Caching {name} from {url} to {cache_path}...")
    try:
        response = requests.get(url)
        response.raise_for_status()
        with open(cache_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        return cache_path
    except Exception as e:
        logger.error(f"Failed to cache {url}: {e}")
        return None

def ingest_docs(custom_source=None):
    data_path = "einstein_ai/data/"
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    documents = []

    # 1. Load from local data directory (including cache)
    logger.info(f"Loading local documents from {data_path}...")

    # Recursive search includes cache/
    txt_loader = DirectoryLoader(
        data_path,
        glob="**/*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents.extend(txt_loader.load())

    pdf_loader = DirectoryLoader(
        data_path,
        glob="**/*.pdf",
        loader_cls=PyPDFLoader
    )
    documents.extend(pdf_loader.load())

    # 2. Handle web sources or custom imports
    if custom_source:
        if custom_source.startswith("http"):
            logger.info(f"Loading from URL: {custom_source}")
            # Cache it first
            cached_file = cache_web_content(custom_source, "CustomSource")
            if cached_file:
                documents.extend(TextLoader(cached_file, encoding="utf-8").load())
            else:
                web_loader = WebBaseLoader(custom_source)
                documents.extend(web_loader.load())
        elif os.path.exists(custom_source):
            if custom_source.endswith(".pdf"):
                documents.extend(PyPDFLoader(custom_source).load())
            else:
                documents.extend(TextLoader(custom_source, encoding="utf-8").load())

    # 3. Load from SOURCES.env
    online_sources = get_online_sources()
    if online_sources:
        for source in online_sources:
            cached_file = cache_web_content(source['url'], source['name'])
            if cached_file:
                # We already loaded local docs, which includes cache.
                # Avoid duplicates.
                pass
            else:
                logger.info(f"Fallback loading {source['name']} directly from {source['url']}...")
                try:
                    web_loader = WebBaseLoader(source['url'])
                    documents.extend(web_loader.load())
                except Exception as e:
                    logger.error(f"Failed to load {source['url']}: {e}")

    # Re-read documents after potential caching to ensure everything is fresh
    # Actually, the logic above is a bit circular. Let's simplify.

    # Clear and reload to be certain
    documents = []
    txt_loader = DirectoryLoader(data_path, glob="**/*.txt", loader_cls=TextLoader, loader_kwargs={"encoding": "utf-8"})
    documents.extend(txt_loader.load())
    pdf_loader = DirectoryLoader(data_path, glob="**/*.pdf", loader_cls=PyPDFLoader)
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

    logger.info("Building FAISS index...")
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("einstein_ai/faiss_index")
    logger.info(f"Successfully created FAISS index with {len(texts)} chunks.")

if __name__ == "__main__":
    import sys
    source = sys.argv[1] if len(sys.argv) > 1 else None
    ingest_docs(source)
