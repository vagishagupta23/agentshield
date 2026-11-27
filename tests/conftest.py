import json
import os

import pytest

from agentshield import tools

os.environ.setdefault("ANTHROPIC_API_KEY", "test-key")


@pytest.fixture
def sent_log(tmp_path, monkeypatch):
    log = tmp_path / "sent.log"
    monkeypatch.setattr(tools, "SENT_LOG", log)
    return log


@pytest.fixture
def inbox(tmp_path, monkeypatch):
    emails = [{"id": "email-001", "from": "priya.nair@veloxa.test", "body": "Hi"}]
    path = tmp_path / "inbox.json"
    path.write_text(json.dumps(emails), encoding="utf-8")
    monkeypatch.setattr(tools, "INBOX_FILE", path)
    return emails
