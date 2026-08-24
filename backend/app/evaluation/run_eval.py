import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[2]))

from app.chains.rag_chain import build_chain, load_retriever
from app.evaluation.test_set import TEST_SET

from datasets import Dataset
from ragas import evaluate
from ragas.metrics import (
    faithfulness,
    answer_relevancy,
    context_precision,
    context_recall,
)
from langchain_huggingface import HuggingFaceEmbeddings
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.run_config import RunConfig
from langchain_ollama import ChatOllama
from langchain_groq import ChatGroq
from dotenv import load_dotenv

load_dotenv()

def run_evaluation():
    print("Loading RAG chain...")
    chain = build_chain()
    retriever = load_retriever()

    questions, references, answers, contexts_list = [], [], [], []

    print(f"Running {len(TEST_SET)} test questions through the chain...\n")

    for i, item in enumerate(TEST_SET, start=1):
        question = item["question"]

        print(f"[{i}/{len(TEST_SET)}] {question}")

        result = chain(question)

        nodes = retriever.retrieve(question)
        retrieved_texts = [n.get_content() for n in nodes]

        questions.append(question)
        references.append(item["reference"])
        answers.append(result["answer"])
        contexts_list.append(retrieved_texts)

    # Build the dataset RAGAS expects
    eval_dataset = Dataset.from_dict({
        "question": questions,
        "answer": answers,
        "contexts": contexts_list,
        "reference": references,
    })

    print(
        "\nRunning RAGAS evaluation "
        "(this uses Ollama as the judge, may take a while)..."
    )

    # Use local Ollama as the judge LLM, and HuggingFace for judge embeddings
    judge_llm = LangchainLLMWrapper(
    ChatGroq(
        model="llama-3.1-8b-instant",
        temperature=0,
    )
)
    judge_embeddings = LangchainEmbeddingsWrapper(
        HuggingFaceEmbeddings(model_name="BAAI/bge-small-en-v1.5")
    )


    results = evaluate(
    eval_dataset,
    metrics=[
        faithfulness,
        answer_relevancy,
        context_precision,
        context_recall,
    ],
    llm=judge_llm,
    embeddings=judge_embeddings,
    run_config=RunConfig(timeout=120, max_workers=4),
)

    print("\n=== RAGAS Evaluation Results ===")
    print(results)

    # Save detailed results
    df = results.to_pandas()

    output_path = (
        Path(__file__).resolve().parent / "eval_results.csv"
    )

    df.to_csv(output_path, index=False)

    print(f"\nDetailed results saved to: {output_path}")


if __name__ == "__main__":
    run_evaluation()