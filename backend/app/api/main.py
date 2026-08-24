from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import json
from pathlib import Path

from app.chains.rag_chain import build_chain

app = FastAPI(title="RAG Papers Assistant API")

# Allow the frontend (running on a different port/domain) to call this API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # we'll tighten this once we know the deployed frontend URL
    allow_methods=["*"],
    allow_headers=["*"],
)

print("Loading RAG chain (this happens once, at startup)...")
rag_chain = build_chain()
print("RAG chain ready.")


class QuestionRequest(BaseModel):
    question: str


class SourceItem(BaseModel):
    label: str
    file_name: str
    score: float | None = None


class AnswerResponse(BaseModel):
    answer: str
    sources: list[SourceItem]


@app.get("/")
def health_check():
    return {"status": "ok", "message": "RAG Papers Assistant API is running"}


@app.post("/chat", response_model=AnswerResponse)
def chat(request: QuestionRequest):
    result = rag_chain(request.question)
    return result

METADATA_FILE = Path(__file__).resolve().parents[2] / "data" / "papers_metadata.json"


@app.get("/papers")
def list_papers():
    with open(METADATA_FILE, "r", encoding="utf-8") as f:
        papers = json.load(f)

    return [
        {
            "arxiv_id": p["arxiv_id"],
            "title": p["title"],
            "pdf_filename": p["pdf_filename"],
            "url": p["url"],
        }
        for p in papers
    ]