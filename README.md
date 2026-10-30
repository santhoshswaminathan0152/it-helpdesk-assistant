# AI-Powered IT Help Desk Assistant

A chat assistant that answers IT service desk questions in real time using **Retrieval-Augmented Generation (RAG)**. Internal technical documentation is converted into a vector database, and the LLM is only allowed to answer from the retrieved documentation, so it gives specific answers instead of hallucinating. If nothing relevant is found, it declines and points the user to the Service Desk.

**Tech stack:** Python · LangChain · Ollama (local LLM) · FAISS vector database · FastEmbed embeddings · Streamlit · Git/GitHub

## Architecture

```
docs/*.md ──► ingest.py ──► split by heading + size ──► embeddings (bge-small) ──► FAISS index (vectorstore/)
                                                                                        │
user question (Streamlit chat, app.py) ──► rag.py ──► top-k similarity search ──────────┘
                                                        │
                                   relevance < threshold? ──yes──► "not in the knowledge base, raise a ticket"
                                                        │ no
                                   prompt (context only) ──► LLM (Ollama) ──► answer + source documents
```

- **Grounded answers:** the prompt restricts the model to the retrieved context, and every answer lists its source documents.
- **Hallucination guard:** chunks below `MIN_RELEVANCE` are discarded. Out-of-scope questions (e.g. "how many days annual leave do I get?") never reach the LLM.
- **Runs locally:** no API keys and no data leaves the machine.

## Project structure

| File | Purpose |
|------|---------|
| `docs/` | Sample internal IT knowledge base (password reset, VPN, email, printers, Wi-Fi, software/hardware) |
| `ingest.py` | Data pipeline: loads markdown docs, chunks them and builds the FAISS vector index |
| `rag.py` | Retrieval + LangChain prompt/LLM chain; also usable from the command line |
| `app.py` | Streamlit chat interface |
| `config.py` | Environment-based settings (`.env`) |
| `tests/` | Pytest tests for chunking, retrieval and the out-of-scope fallback |

## Getting started

```bash
# 1. Install and start Ollama (https://ollama.com/download), then pull a model
ollama pull qwen2.5:0.5b        # small and fast; use llama3.2:3b or qwen2.5:7b for better answers

# 2. Install dependencies
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env            # optional: change model, threshold, etc.

# 3. Build the vector database from docs/
python ingest.py

# 4. Launch the chat app
streamlit run app.py
```

Ask from the command line:

```bash
python rag.py "VPN says authentication failed"
```

Run the tests:

```bash
pytest -q
```

## Using your own documentation

Drop markdown files into `docs/` and run `python ingest.py` again, or click **Rebuild index** in the app sidebar. Headings (`#`, `##`) become chunk boundaries, so well-structured docs retrieve best.

## Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_MODEL` | `qwen2.5:0.5b` | Any chat model pulled into Ollama |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `EMBEDDING_MODEL` | `BAAI/bge-small-en-v1.5` | FastEmbed embedding model |
| `TOP_K` | `4` | Chunks retrieved per question |
| `MIN_RELEVANCE` | `0.5` | Minimum relevance score (0–1) for a chunk to be used |

## Example

> **Q:** How do I reset my password?
> **A:** 1. Go to the self-service portal at https://passwordreset.company.local. 2. Enter your corporate email address and complete the MFA challenge… *(Sources: password_reset.md)*

> **Q:** How many days annual leave do I get?
> **A:** I couldn't find this in the IT knowledge base, so I won't guess. Please raise a ticket in the IT portal or call the Service Desk on extension 4357.

> Note: the documents in `docs/` are sample content written for this demo; the URLs and extensions are placeholders.
