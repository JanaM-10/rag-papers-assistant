from pathlib import Path
from llama_index.core import SimpleDirectoryReader
from llama_index.core.node_parser import SentenceSplitter
from collections import Counter

PAPERS_DIR = Path(__file__).resolve().parents[2] / "data" / "papers"

print("Loading PDFs...")
documents = SimpleDirectoryReader(input_dir=str(PAPERS_DIR)).load_data()
print(f"Loaded {len(documents)} document objects (LlamaIndex creates one per page).")

# Count pages per source file — a wildly uneven count points to the bad file
file_counts = Counter(doc.metadata.get("file_name", "unknown") for doc in documents)
print("\nPages loaded per file:")
for fname, count in file_counts.most_common():
    print(f"  {fname}: {count}")

# Now chunk (no embedding) and see where the explosion happens
splitter = SentenceSplitter(chunk_size=512, chunk_overlap=64)
nodes = splitter.get_nodes_from_documents(documents)
print(f"\nTotal chunks after splitting: {len(nodes)}")

chunk_file_counts = Counter(n.metadata.get("file_name", "unknown") for n in nodes)
print("\nChunks per file:")
for fname, count in chunk_file_counts.most_common():
    print(f"  {fname}: {count}")

# Peek at the worst offender's raw text
worst_file = chunk_file_counts.most_common(1)[0][0]
print(f"\nSample text from worst offender ({worst_file}):")
sample_nodes = [n for n in nodes if n.metadata.get("file_name") == worst_file][:3]
for i, n in enumerate(sample_nodes):
    print(f"\n--- chunk {i} ---")
    print(repr(n.text[:300]))