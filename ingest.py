"""Convert the IT knowledge base in docs/ into a FAISS vector index."""
from pathlib import Path

from langchain_community.vectorstores import FAISS
from langchain_text_splitters import MarkdownHeaderTextSplitter, RecursiveCharacterTextSplitter

from config import DOCS_DIR, INDEX_DIR, get_embeddings

HEADERS = [("#", "title"), ("##", "section")]


def load_chunks(docs_dir: Path = DOCS_DIR):
    header_splitter = MarkdownHeaderTextSplitter(HEADERS, strip_headers=False)
    size_splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
    chunks = []
    for path in sorted(docs_dir.glob("*.md")):
        for chunk in size_splitter.split_documents(header_splitter.split_text(path.read_text())):
            chunk.metadata["source"] = path.name
            chunks.append(chunk)
    return chunks


def build_index(docs_dir: Path = DOCS_DIR, index_dir: Path = INDEX_DIR):
    chunks = load_chunks(docs_dir)
    if not chunks:
        raise SystemExit(f"No markdown documents found in {docs_dir}")
    store = FAISS.from_documents(chunks, get_embeddings())
    store.save_local(str(index_dir))
    print(f"Indexed {len(chunks)} chunks from {docs_dir} into {index_dir}")
    return store


if __name__ == "__main__":
    build_index()
