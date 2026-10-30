import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

ROOT = Path(__file__).parent
DOCS_DIR = ROOT / "docs"
INDEX_DIR = ROOT / "vectorstore"

OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "BAAI/bge-small-en-v1.5")
TOP_K = int(os.getenv("TOP_K", "4"))
# Chunks scoring below this relevance (0-1) are ignored; if none remain the bot declines to answer.
MIN_RELEVANCE = float(os.getenv("MIN_RELEVANCE", "0.5"))


def get_embeddings():
    from langchain_community.embeddings import FastEmbedEmbeddings

    return FastEmbedEmbeddings(model_name=EMBEDDING_MODEL)
