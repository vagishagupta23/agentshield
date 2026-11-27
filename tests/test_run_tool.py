import json

from agentshield.agent import run_tool


def test_unknown_tool():
    assert run_tool("delete_inbox", {}) == ("Unknown tool: delete_inbox", True)


def test_invalid_arguments():
    assert run_tool("read_doc", {"file": "refund_policy.md"}) == ("Invalid tool arguments.", True)


def test_path_traversal_is_an_error():
    output, is_error = run_tool("read_doc", {"name": "../../.env"})
    assert is_error
    assert "Access denied" in output


def test_missing_file_hides_the_path():
    assert run_tool("read_doc", {"name": "missing.md"}) == (
        "File not found or could not be read.",
        True,
    )


def test_list_results_are_json(inbox):
    output, is_error = run_tool("read_inbox", {})
    assert not is_error
    assert json.loads(output) == inbox


def test_send_email(sent_log):
    output, is_error = run_tool(
        "send_email", {"to": "a@veloxa.test", "subject": "hi", "body": "hello"}
    )
    assert (output, is_error) == ("Email sent to a@veloxa.test", False)
    assert sent_log.exists()
