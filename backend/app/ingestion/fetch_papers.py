import arxiv
import os
import json
from pathlib import Path
from urllib.request import urlretrieve

# Where papers and their metadata will be saved
DATA_DIR = Path(__file__).resolve().parents[2] / "data" / "papers"
DATA_DIR.mkdir(parents=True, exist_ok=True)
METADATA_FILE = DATA_DIR.parent / "papers_metadata.json"

# Search queries covering the topics we want in the knowledge base
SEARCH_QUERIES = [
    "retrieval augmented generation",
    "large language model agents",
    "fine-tuning large language models",
]

PAPERS_PER_QUERY = 7  # ~21 papers total across 3 queries


def fetch_papers():
    client = arxiv.Client()
    all_metadata = []
    seen_ids = set()

    for query in SEARCH_QUERIES:
        print(f"Searching arXiv for: '{query}'")
        search = arxiv.Search(
            query=query,
            max_results=PAPERS_PER_QUERY,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        for result in client.results(search):
            arxiv_id = result.get_short_id()
            if arxiv_id in seen_ids:
                continue
            seen_ids.add(arxiv_id)

            # Download the PDF
            filename = f"{arxiv_id.replace('/', '_')}.pdf"
            filepath = DATA_DIR / filename
            print(f"  Downloading: {result.title[:70]}...")
            urlretrieve(result.pdf_url, str(filepath))

            # Save metadata for citations later
            all_metadata.append({
                "arxiv_id": arxiv_id,
                "title": result.title,
                "authors": [a.name for a in result.authors],
                "published": str(result.published.date()),
                "pdf_filename": filename,
                "url": result.entry_id,
                "summary": result.summary,
            })

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(all_metadata, f, indent=2, ensure_ascii=False)

    print(f"\nDone. Downloaded {len(all_metadata)} papers.")
    print(f"Metadata saved to: {METADATA_FILE}")


if __name__ == "__main__":
    fetch_papers()