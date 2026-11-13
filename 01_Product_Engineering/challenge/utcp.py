"""TC5 second implementation: UTCP.

The model reaches `get_incident` through a tool generated from use_case/api.json.
The incident API is the stand-in route in app.py, reached in-process (no network hop).
"""

import json

import httpx2
from fastmcp import Client, FastMCP
from fastmcp.server.middleware import Middleware
from litellm import completion
from pydantic import ValidationError

import llm
from app import app  # the Gradio Server is an ASGI app, so it can be called in-process
from classifier import _PROMPT_BEFORE_CATEGORIES, _PROMPT_RULES, apply_review_policy, build_system_prompt, load_taxonomy
from incidents import USE_CASE_DIR
from schema import BatchIntItem, BatchIntResponse, SingleIntResponse

SPEC = json.loads((USE_CASE_DIR / "api.json").read_text())

# Same as classifier._PROMPT_INTRO except rule 2: the model fetches the record itself.
_PROMPT_INTRO_UTCP = """1. You are a classifier for incidents.
2a. You will be given an incident Id and you will fetch the incident details from the get_incident tool.
2b. You will classify the fetched incident into a category.
The definition of a not_toil task is as follows:
"""

# Option B: several incidents in one conversation, so the model can fetch them in one turn.
_PROMPT_INTRO_BATCH = """1. You are a classifier for incidents.
2a. You will be given several incident Ids. Fetch each one with the get_incident tool.
2b. Classify each fetched incident separately, applying every rule below to each incident on its own.
2c. Return one classification per incident, each with its incident_id, together in a single JSON object.
The definition of a not_toil task is as follows:
"""


def build_batch_prompt(taxonomy: dict) -> str:
    """Same rules as build_system_prompt, but asks for a BatchIntResponse."""
    not_toil = taxonomy["not_toil"]
    categories = "\n".join(f"{c['name']}: {c['description']}" for c in taxonomy["categories"])
    return (
        _PROMPT_INTRO_BATCH
        + f"{not_toil['name']}: {not_toil['description']}\n"
        + _PROMPT_BEFORE_CATEGORIES
        + categories + "\n"
        + _PROMPT_RULES
        + json.dumps(BatchIntResponse.model_json_schema(), indent=2) + "\n"
    )


class FetchLog(Middleware):
    """Records which incident ids get_incident actually returned. The model choosing whether to fetch
    is the risk UTCP adds: on emulated tool calling it classified an incident it never fetched."""

    def __init__(self):
        self.ids = set()

    async def on_call_tool(self, context, call_next):
        result = await call_next(context)  # a failed fetch raises here, so it is never recorded
        if context.message.name.endswith("get_incident"):
            self.ids.add((context.message.arguments or {}).get("incident_id"))
        return result


class NotFetched(ValueError):
    """A classification for an incident the model never fetched: evidence missing, so the answer is invalid."""


def require_fetched(fetched: set, incident_ids: list[str]) -> None:
    missing = [incident_id for incident_id in incident_ids if incident_id not in fetched]
    if missing:
        raise NotFetched(f"You classified {', '.join(missing)} without fetching the record.")


def retry_message(error: ValueError) -> str:
    """What the model is told after an invalid answer. A missing fetch needs a tool call, not just new JSON."""
    if isinstance(error, NotFetched):
        return f"{error} Call get_incident for each incident you have not fetched, then return the classification as JSON."
    problems = ([{"field": err["loc"], "problem": err["msg"]} for err in error.errors()]
                if isinstance(error, ValidationError) else [{"problem": str(error)}])
    return f"That response was invalid: {json.dumps(problems, default=str)}. Return corrected JSON only."


def incident_client(token="issued-to-toilmap"):
    return httpx2.AsyncClient(
        transport=httpx2.ASGITransport(app=app),
        base_url="https://incidents.internal",
        headers={"Authorization": f"Bearer {token}"},
    )

def openai_tools(mcp_tools) -> list[dict]:
    """MCP tool listings in the shape a chat-completions API expects."""
    return [{"type": "function", "function": {
        "name": tool.name, "description": tool.description or "", "parameters": tool.input_schema,
    }} for tool in mcp_tools]

async def dispatch(client, call) -> str:
    """Run one tool call through the MCP client. Failures are returned, never raised."""
    try:
        arguments = json.loads(call.function.arguments or "{}")
    except ValueError as error:
        return f"arguments were not a JSON object: {error}"
    result = await client.call_tool(call.function.name, arguments, raise_on_error=False)
    text = "\n".join(getattr(block, "text", "") for block in result.content)
    if result.is_error and text.startswith("Unknown tool"):  # say what is wrong AND what is right
        text += ". Available tools: " + ", ".join(tool.name for tool in await client.list_tools())
    return text

async def run_agent(client, messages: list[dict], meter=None, first_choice: str = "auto") -> tuple[str, list[dict]]:
    """Decide, dispatch, answer: the whole loop, over any MCP client.
    Returns the final text and the conversation so far, so a retry keeps the fetched record in context."""
    tools = openai_tools(await client.list_tools())
    messages = list(messages)
    for round_number in range(6):
        reply = completion(**llm.call_kwargs(llm.MODEL, messages), tools=tools,
                           tool_choice=first_choice if round_number == 0 else "auto")
        if meter:
            meter.track(reply)
        message = reply.choices[0].message
        if not message.tool_calls:
            return message.content or "", messages
        messages.append(message.model_dump())
        for call in message.tool_calls:
            messages.append({"role": "tool", "tool_call_id": call.id, "content": await dispatch(client, call)})
    return "gave up after 6 rounds", messages

async def call_with_utcp(incident_id: str, meter=None, counter=None) -> dict:
    """Same contract as the classify_incident endpoint: validated, retried once, review policy applied.
    An answer for an incident that was never fetched counts as invalid."""
    described = FastMCP.from_openapi(SPEC, client=incident_client(), name="incidents")
    fetch_log = FetchLog()
    described.add_middleware(fetch_log)
    if counter:
        described.add_middleware(counter)
    taxonomy = load_taxonomy()
    messages = [
        {"role": "system", "content": build_system_prompt(taxonomy, intro=_PROMPT_INTRO_UTCP)},
        {"role": "user", "content": f"Classify incident {incident_id}."},
    ]
    async with Client(described) as c:
        for _ in range(2):
            raw, messages = await run_agent(c, messages, meter)
            try:
                response = SingleIntResponse.model_validate_json(raw)
                require_fetched(fetch_log.ids, [incident_id])
                return {"answer": apply_review_policy(response, taxonomy).model_dump_json()}
            except ValueError as e:  # pydantic's ValidationError is a ValueError too
                messages = messages + [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content": retry_message(e)},
                ]
    # Same fallback as the endpoint in app.py: a failure routes to a person.
    return {"answer": SingleIntResponse(
        needs_human=True,
        confidence=0,
        reason="Classification failed: model output was invalid after a retry. Route to human review.",
    ).model_dump_json()}


def validate_batch(raw: str, incident_ids: list[str], taxonomy: dict, fetched: set) -> BatchIntResponse:
    """Schema-valid is not enough: 2 results for 3 incidents passes pydantic, and so does a result
    for an incident never fetched. Check the ids against both."""
    batch = BatchIntResponse.model_validate_json(raw)
    returned = [item.incident_id for item in batch.classifications]
    if sorted(returned) != sorted(incident_ids):
        raise ValueError(f"expected exactly one classification for each of {incident_ids}, got {returned}")
    require_fetched(fetched, incident_ids)
    return batch.model_copy(update={
        "classifications": [apply_review_policy(item, taxonomy) for item in batch.classifications],
    })


async def call_with_utcp_batch(incident_ids: list[str], meter=None, counter=None) -> dict:
    """Option B: one conversation for several incidents. Retried once, then every incident routes to a person."""
    described = FastMCP.from_openapi(SPEC, client=incident_client(), name="incidents")
    fetch_log = FetchLog()
    described.add_middleware(fetch_log)
    if counter:
        described.add_middleware(counter)
    taxonomy = load_taxonomy()
    messages = [
        {"role": "system", "content": build_batch_prompt(taxonomy)},
        {"role": "user", "content": f"Classify incidents {', '.join(incident_ids)}."},
    ]
    async with Client(described) as c:
        for _ in range(2):
            raw, messages = await run_agent(c, messages, meter)
            try:
                return {"answer": validate_batch(raw, incident_ids, taxonomy, fetch_log.ids).model_dump_json()}
            except ValueError as e:  # pydantic's ValidationError is a ValueError too
                messages = messages + [
                    {"role": "assistant", "content": raw},
                    {"role": "user", "content": retry_message(e)},
                ]
    return {"answer": BatchIntResponse(classifications=[
        BatchIntItem(
            incident_id=incident_id,
            needs_human=True,
            confidence=0,
            reason="Classification failed: batch output was invalid after a retry. Route to human review.",
        ) for incident_id in incident_ids
    ]).model_dump_json()}
