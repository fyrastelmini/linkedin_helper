import pytest
from summarizer import summarize

def test_summarize():
    text = "This is a test text for the summarizer function."
    summary = summarize(text)

    # Check that the function returns a string
    assert isinstance(summary, str)

    # Check that the summary is not empty
    assert len(summary) > 0