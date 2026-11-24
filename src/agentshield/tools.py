import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parents[2] / "data"
SENT_LOG = DATA_DIR.parent / "sent.log"


def read_inbox() -> list[dict]:
    inbox_file = DATA_DIR / "inbox.json"
    with open(inbox_file, "r", encoding="utf-8") as file:
        data = json.load(file)
    return data


def _read_file(folder: str, name: str) -> str:
    base = (DATA_DIR / folder).resolve()
    path = (base / name).resolve()

    if not path.is_relative_to(base):
        raise ValueError(f"Access denied: {name}")

    return path.read_text(encoding="utf-8")


def read_doc(name: str) -> str:
    return _read_file("docs", name)


def fetch_page(name: str) -> str:
    return _read_file("pages", name)


def send_email(to: str, subject: str, body: str) -> str:
    email = {"to": to, "subject": subject, "body": body}
    with open(SENT_LOG, "a", encoding="utf-8") as file:
        file.write(json.dumps(email) + "\n")
    return f"Email sent to {to}"


if __name__ == "__main__":
    print(read_inbox())
    print(read_doc("refund_policy.md"))
    print(fetch_page("pricing.html"))
