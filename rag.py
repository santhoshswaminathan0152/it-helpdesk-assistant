"""Retrieval-augmented answering for IT service desk questions."""
from langchain_community.vectorstores import FAISS
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from langchain_ollama import ChatOllama

from config import INDEX_DIR, MIN_RELEVANCE, OLLAMA_BASE_URL, OLLAMA_MODEL, TOP_K, get_embeddings

FALLBACK = (
    "I couldn't find this in the IT knowledge base, so I won't guess. "
    "Please raise a ticket in the IT portal or call the Service Desk on extension 4357."
)

PROMPT = ChatPromptTemplate.from_messages([
    ("system",
     "You are an IT service desk assistant. Answer the user's question using ONLY the context below. "
     "If the context does not contain the answer, reply exactly: \"" + FALLBACK + "\" "
     "Keep answers short and give numbered steps where the context has them. "
     "Never invent URLs, phone numbers or policies.\n\nContext:\n{context}"),
    ("human", "{question}"),
])


class HelpDeskAssistant:
    def __init__(self):
        self.store = FAISS.load_local(str(INDEX_DIR), get_embeddings(), allow_dangerous_deserialization=True)
        llm = ChatOllama(model=OLLAMA_MODEL, base_url=OLLAMA_BASE_URL, temperature=0)
        self.chain = PROMPT | llm | StrOutputParser()

    def retrieve(self, question: str):
        results = self.store.similarity_search_with_relevance_scores(question, k=TOP_K)
        return [(doc, score) for doc, score in results if score >= MIN_RELEVANCE]

    def answer(self, question: str) -> dict:
        hits = self.retrieve(question)
        if not hits:
            return {"answer": FALLBACK, "sources": []}
        context = "\n\n---\n\n".join(doc.page_content for doc, _ in hits)
        sources = sorted({doc.metadata["source"] for doc, _ in hits})
        return {"answer": self.chain.invoke({"context": context, "question": question}), "sources": sources}


if __name__ == "__main__":
    import sys

    result = HelpDeskAssistant().answer(" ".join(sys.argv[1:]) or "How do I reset my password?")
    print(result["answer"])
    print("Sources:", ", ".join(result["sources"]) or "none")
