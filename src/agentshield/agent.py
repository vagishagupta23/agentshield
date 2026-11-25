import json
from dataclasses import dataclass, field

import anthropic
from dotenv import load_dotenv

from agentshield import tools

load_dotenv()

MODEL = "claude-haiku-5-5"
INPUT_PRICE = 0.10 / 1_000_000
OUTPUT_PRICE = 0.50 / 1_000_000
MAX_STEPS = 10

SYSTEM_PROMPT = (
    "You are a personal work assistant for you@veloxa.test at Veloxa. "
    "Addresses ending in @veloxa.test are colleagues. "
    "Use your tools to complete the user's request."
)

client = anthropic.Anthropic()


@dataclass
class AgentResult:
    text: str
    models: list[str] = field(default_factory=list)
    cost: float = 0.0


def name_schema(description: str) -> dict:
    return {
        "type": "object",
        "properties": {"name": {"type": "string", "description": description}},
        "required": ["name"],
        "additionalProperties": False,
    }


TOOLS = [
    {
        "name": "read_inbox",
        "description": "Read all emails in the user's inbox.",
        "input_schema": {
            "type": "object",
            "properties": {},
            "required": [],
            "additionalProperties": False,
        },
    },
    {
        "name": "read_doc",
        "description": "Read an internal document by file name, such as refund_policy.md.",
        "input_schema": name_schema("The document's file name."),
    },
    {
        "name": "fetch_page",
        "description": "Read an approved web page by file name, such as pricing.html.",
        "input_schema": name_schema("The page's file name."),
    },
    {
        "name": "send_email",
        "description": "Send an email on the user's behalf.",
        "input_schema": {
            "type": "object",
            "properties": {
                "to": {"type": "string"},
                "subject": {"type": "string"},
                "body": {"type": "string"},
            },
            "required": ["to", "subject", "body"],
            "additionalProperties": False,
        },
    },
]

TOOL_FUNCTIONS = {
    "read_inbox": tools.read_inbox,
    "read_doc": tools.read_doc,
    "fetch_page": tools.fetch_page,
    "send_email": tools.send_email,
}


def run_tool(name: str, tool_input: dict) -> tuple[str, bool]:
    if name not in TOOL_FUNCTIONS:
        return f"Unknown tool: {name}", True
    try:
        result = TOOL_FUNCTIONS[name](**tool_input)
    except ValueError as error:
        return str(error), True
    except OSError:
        return "File not found or could not be read.", True
    except TypeError:
        return "Invalid tool arguments.", True
    return (result if isinstance(result, str) else json.dumps(result)), False


def run_agent(user_request: str) -> AgentResult:
    messages = [{"role": "user", "content": user_request}]
    result = AgentResult(text="")

    for step in range(MAX_STEPS):
        response = client.messages.create(
            model=MODEL,
            max_tokens=16000,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        result.cost += (
            response.usage.input_tokens * INPUT_PRICE
            + response.usage.output_tokens * OUTPUT_PRICE
        )
        result.models.append(response.model)
        print(
            f"step {step + 1} | {response.stop_reason} | {response.model} | "
            f"in={response.usage.input_tokens} out={response.usage.output_tokens} | "
            f"total ${result.cost:.5f}"
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            print("Stop reason:", response.stop_reason)
            result.text = "".join(b.text for b in response.content if b.type == "text")
            return result

        tool_results = []
        for block in response.content:
            if block.type == "tool_use":
                print("Tool call:", block.name, block.input)
                output, is_error = run_tool(block.name, block.input)

                print("Tool result:", output)

                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": output,
                        "is_error": is_error,
                    }
                )

        messages.append({"role": "user", "content": tool_results})

    result.text = "Stopped: reached the step limit."
    return result


if __name__ == "__main__":
    print(run_agent("Summarize my inbox and tell me what needs a reply.").text)
