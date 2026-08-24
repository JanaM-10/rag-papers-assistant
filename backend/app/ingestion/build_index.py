import os
from pathlib import Path
from llama_index.core import (
    SimpleDirectoryReader,
    VectorStoreIndex,
    StorageContext,
    Settings,
)
from llama_index.core.node_parser import SentenceSplitter
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore
from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client
import chromadb
from dotenv import load_dotenv

load_dotenv()

# Paths
BASE_DIR = Path(__file__).resolve().parents[2]
PAPERS_DIR = BASE_DIR / "data" / "papers"
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
CHROMA_DIR.mkdir(parents=True, exist_ok=True)

COLLECTION_NAME = "papers_collection"
VECTOR_STORE_PROVIDER = os.getenv("VECTOR_STORE_PROVIDER", "chroma")  # "chroma" or "qdrant"


def build_index():
    print("Loading PDFs...")
    documents = SimpleDirectoryReader(input_dir=str(PAPERS_DIR)).load_data()
    print(f"Loaded {len(documents)} document objects (one per page, typically).")

    print("Setting up embedding model (this downloads the model on first run)...")
    Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")

    Settings.node_parser = SentenceSplitter(chunk_size=512, chunk_overlap=64)

    if VECTOR_STORE_PROVIDER == "qdrant":
        print("Setting up Qdrant Cloud vector store...")
        client = qdrant_client.QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    else:
        print("Setting up local Chroma vector store...")
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    storage_context = StorageContext.from_defaults(vector_store=vector_store)

    print("Building index (this will take a few minutes)...")
    index = VectorStoreIndex.from_documents(
        documents,
        storage_context=storage_context,
        show_progress=True,
    )

    print(f"\nDone. Index built using provider: {VECTOR_STORE_PROVIDER}")
    if VECTOR_STORE_PROVIDER == "chroma":
        print(f"Chroma collection '{COLLECTION_NAME}' contains {chroma_collection.count()} chunks.")

    return index


if __name__ == "__main__":
    build_index()