import json

import pytest

from agentshield import tools


def test_read_inbox_returns_emails(inbox):
    assert tools.read_inbox() == inbox


def test_read_doc_returns_contents():
    assert "Refund Policy" in tools.read_doc("refund_policy.md")


def test_fetch_page_returns_contents():
    assert "Veloxa Pricing" in tools.fetch_page("pricing.html")


@pytest.mark.parametrize(
    "name",
    ["../inbox.json", "../../pyproject.toml", "/etc/passwd", "../../.env"],
)
def test_read_doc_blocks_paths_outside_docs(name):
    with pytest.raises(ValueError, match="Access denied"):
        tools.read_doc(name)


def test_fetch_page_cannot_reach_docs():
    with pytest.raises(ValueError, match="Access denied"):
        tools.fetch_page("../docs/secrets.md")


def test_read_doc_missing_file():
    with pytest.raises(FileNotFoundError):
        tools.read_doc("missing.md")


def test_send_email_appends_to_log(sent_log):
    assert tools.send_email("a@veloxa.test", "one", "first") == "Email sent to a@veloxa.test"
    tools.send_email("b@veloxa.test", "two", "second")

    emails = [json.loads(line) for line in sent_log.read_text().splitlines()]
    assert emails == [
        {"to": "a@veloxa.test", "subject": "one", "body": "first"},
        {"to": "b@veloxa.test", "subject": "two", "body": "second"},
    ]
