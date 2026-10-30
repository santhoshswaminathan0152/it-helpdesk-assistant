import streamlit as st

from config import INDEX_DIR, OLLAMA_MODEL
from ingest import build_index
from rag import HelpDeskAssistant

st.set_page_config(page_title="IT Help Desk Assistant", page_icon="🛠️")
st.title("🛠️ IT Help Desk Assistant")
st.caption(f"Answers come only from the internal IT knowledge base · model: {OLLAMA_MODEL}")


@st.cache_resource(show_spinner="Loading knowledge base...")
def get_assistant():
    if not (INDEX_DIR / "index.faiss").exists():
        build_index()
    return HelpDeskAssistant()


with st.sidebar:
    st.subheader("Knowledge base")
    if st.button("Rebuild index from docs/"):
        build_index()
        get_assistant.clear()
        st.success("Index rebuilt.")
    if st.button("Clear chat"):
        st.session_state.messages = []
    st.markdown("**Try asking:**\n- How do I reset my password?\n- VPN says authentication failed\n- My print job is stuck")

assistant = get_assistant()
st.session_state.setdefault("messages", [])

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("sources"):
            st.caption("Sources: " + ", ".join(msg["sources"]))

if question := st.chat_input("Describe your IT issue..."):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)
    with st.chat_message("assistant"):
        with st.spinner("Searching the knowledge base..."):
            result = assistant.answer(question)
        st.markdown(result["answer"])
        if result["sources"]:
            st.caption("Sources: " + ", ".join(result["sources"]))
    st.session_state.messages.append({"role": "assistant", "content": result["answer"], "sources": result["sources"]})
