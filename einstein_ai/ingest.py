import os
from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

def ingest_docs():
    data_path = "einstein_ai/data/"

    # Check if data directory exists
    if not os.path.exists(data_path):
        print(f"Error: Data directory not found at {data_path}")
        return

    # Explicitly set encoding to utf-8 for Windows compatibility.
    # We use loader_kwargs to pass the encoding parameter to the underlying TextLoader.
    print(f"Loading documents from {data_path}...")
    loader = DirectoryLoader(
        data_path,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"}
    )

    try:
        documents = loader.load()
    except Exception as e:
        print(f"Error during document loading: {e}")
        return

    if not documents:
        print("No documents found to index.")
        return

    print(f"Splitting {len(documents)} documents into chunks...")
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)
    texts = text_splitter.split_documents(documents)

    print("Initializing embeddings model...")
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

    print("Building FAISS index...")
    db = FAISS.from_documents(texts, embeddings)
    db.save_local("einstein_ai/faiss_index")
    print(f"Successfully created FAISS index with {len(texts)} chunks.")

if __name__ == "__main__":
    ingest_docs()
