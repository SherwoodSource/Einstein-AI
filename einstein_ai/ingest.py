import os
# Set USER_AGENT at the very top to avoid warnings from LangChain/HuggingFace
os.environ["USER_AGENT"] = "EinsteinAI/1.0 (Retriever Bot)"

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

# Predefined online sources to replace local large files
ONLINE_SOURCES = {
    "relativity": "https://www.gutenberg.org/cache/epub/30155/pg30155.txt",
    "meaning": "https://www.gutenberg.org/cache/epub/50531/pg50531.txt"
}

def ingest_docs(custom_source=None):
    data_path = "einstein_ai/data/"
    if not os.path.exists(data_path):
        os.makedirs(data_path)

    documents = []

    # 1. Load from local data directory (txt, pdf)
    logger.info(f"Loading local documents from {data_path}...")

    # Text files
    txt_loader = DirectoryLoader(
        data_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )
    documents.extend(txt_loader.load())

    # PDF files
    pdf_loader = DirectoryLoader(
        data_path,
        glob="*.pdf",
        loader_cls=PyPDFLoader
    )
    documents.extend(pdf_loader.load())

    # 2. Handle web sources or custom imports
    if custom_source:
        if custom_source.startswith("http"):
            logger.info(f"Loading from URL: {custom_source}")
            web_loader = WebBaseLoader(custom_source)
            documents.extend(web_loader.load())
        elif os.path.exists(custom_source):
            if custom_source.endswith(".pdf"):
                documents.extend(PyPDFLoader(custom_source).load())
            else:
                documents.extend(TextLoader(custom_source, encoding="utf-8").load())

    # If no local docs and no custom source, load from default online sources
    if not documents and not custom_source:
        logger.info("No local documents found. Loading from online sources...")
        for key, url in ONLINE_SOURCES.items():
            logger.info(f"Loading {key} from {url}...")
            web_loader = WebBaseLoader(url)
            documents.extend(web_loader.load())

    if not documents:
        logger.warning("No documents found to index.")
        return

    # Use smaller chunk size to stay within model context limits (TinyLlama 2048)
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
