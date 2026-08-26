from dotenv import load_dotenv
load_dotenv()

from pathlib import Path
import chromadb

from llama_index.core import VectorStoreIndex, Settings
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.vector_stores.chroma import ChromaVectorStore

import os

from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

from llama_index.vector_stores.qdrant import QdrantVectorStore
import qdrant_client

BASE_DIR = Path(__file__).resolve().parents[2]
CHROMA_DIR = BASE_DIR / "data" / "chroma_db"
COLLECTION_NAME = "papers_collection"

TOP_K = 5 # how many chunks to retrieve per query


VECTOR_STORE_PROVIDER = os.getenv("VECTOR_STORE_PROVIDER", "chroma")  # "chroma" (local) or "qdrant" (production)

def load_retriever():
    """Reconnects to the existing vector index — local Chroma or cloud Qdrant depending on env."""

    if VECTOR_STORE_PROVIDER == "qdrant":
        # Production: use HF's hosted Inference API so we don't load torch/the model
        # in-process (Render's free tier has a 512MB memory limit)
        from llama_index.embeddings.huggingface_api import HuggingFaceInferenceAPIEmbedding
        Settings.embed_model = HuggingFaceInferenceAPIEmbedding(
            model_name="BAAI/bge-small-en-v1.5",
            token=os.getenv("HF_TOKEN"),
        )
        client = qdrant_client.QdrantClient(
            url=os.getenv("QDRANT_URL"),
            api_key=os.getenv("QDRANT_API_KEY"),
        )
        vector_store = QdrantVectorStore(client=client, collection_name=COLLECTION_NAME)
    else:
        # Local dev: load the model in-process, memory isn't a constraint on your machine
        Settings.embed_model = HuggingFaceEmbedding(model_name="BAAI/bge-small-en-v1.5")
        chroma_client = chromadb.PersistentClient(path=str(CHROMA_DIR))
        chroma_collection = chroma_client.get_or_create_collection(COLLECTION_NAME)
        vector_store = ChromaVectorStore(chroma_collection=chroma_collection)

    index = VectorStoreIndex.from_vector_store(vector_store)
    return index.as_retriever(similarity_top_k=TOP_K)

def format_docs_with_sources(nodes):
    """Turns retrieved LlamaIndex nodes into a context string + a sources list."""
    context_parts = []
    sources = []

    labels = ["A", "B", "C", "D", "E", "F", "G", "H"]

    for i, node in enumerate(nodes):
        label = labels[i] if i < len(labels) else str(i)

        file_name = node.metadata.get("file_name", "unknown")

        context_parts.append(
            f"[DOCUMENT {label} — {file_name}]\n"
            f"{node.get_content()}"
        )

        sources.append({
            "label": label,
            "file_name": file_name,
            "score": round(node.score, 3) if node.score else None
        })

    return "\n\n---\n\n".join(context_parts), sources


PROMPT = ChatPromptTemplate.from_messages([
    (
        "system",
        "You are a research assistant answering questions about AI/ML papers. "
        "Use ONLY the provided context to answer. The context is divided into "
        "labeled documents like [DOCUMENT A], [DOCUMENT B], etc. "
        "When citing, refer ONLY to these document labels (A, B, C...) — never invent "
        "or reference numbered citations that appear inside the document text itself, "
        "those are from the original papers' own bibliographies and are irrelevant here. "
        "If the context doesn't contain the answer, say so clearly instead of guessing."
    ),
    (
        "human",
        "Context:\n{context}\n\nQuestion: {question}"
    ),
])

LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" (local) or "groq" (production)

if LLM_PROVIDER == "groq":
    llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.1)
else:
    llm = ChatOllama(model="llama3.2:1b", temperature=0.1)
def build_chain():
    retriever = load_retriever()

    def retrieve_and_format(question: str):
        nodes = retriever.retrieve(question)
        context, sources = format_docs_with_sources(nodes)
        return {"context": context, "question": question, "_sources": sources}

    chain = (
        RunnablePassthrough()
        | retrieve_and_format
    )

    # Separate the generation part so we can still access `_sources` after
    def run(question: str):
        data = retrieve_and_format(question)
        prompt_value = PROMPT.invoke({"context": data["context"], "question": data["question"]})
        answer = (llm | StrOutputParser()).invoke(prompt_value)
        return {"answer": answer, "sources": data["_sources"]}

    return run


if __name__ == "__main__":
    chain = build_chain()
    while True:
        question = input("\nAsk a question (or 'quit'): ")
        if question.lower() == "quit":
            break
        result = chain(question)
        print(f"\nAnswer:\n{result['answer']}")
        print(f"\nSources used:")
        for s in result["sources"]:
            print(f"  - {s['file_name']} (relevance: {s['score']})")