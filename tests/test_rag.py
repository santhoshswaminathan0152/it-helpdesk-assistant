import pytest

from ingest import build_index, load_chunks
from rag import FALLBACK, HelpDeskAssistant


def test_every_doc_is_chunked_with_source():
    chunks = load_chunks()
    assert {c.metadata["source"] for c in chunks} >= {"password_reset.md", "vpn.md", "printer.md"}


@pytest.fixture(scope="module")
def assistant(tmp_path_factory, monkeypatch_module):
    index_dir = tmp_path_factory.mktemp("index")
    monkeypatch_module.setattr("rag.INDEX_DIR", index_dir)
    build_index(index_dir=index_dir)
    return HelpDeskAssistant()


@pytest.fixture(scope="module")
def monkeypatch_module():
    with pytest.MonkeyPatch.context() as mp:
        yield mp


def test_relevant_question_retrieves_matching_doc(assistant):
    hits = assistant.retrieve("How do I reset my password?")
    assert hits and hits[0][0].metadata["source"] == "password_reset.md"


def test_out_of_scope_question_is_declined_without_calling_llm(assistant):
    assert assistant.answer("What is the capital of France?") == {"answer": FALLBACK, "sources": []}
