"""The model call.

One function, one job: take a conversation, stream back the assistant's reply.

Everything provider-specific lives in environment variables, so switching from
OpenAI to Azure to a self-hosted model is a config change, not a code change.
That property matters more than it looks like it does right now -- see the
"Where does this live?" section of the README.
"""

import json
import os

from litellm import completion, get_model_info, token_counter

# LiteLLM picks the provider from the model string:
#   "gpt-4.1-mini"                    -> OpenAI
#   "azure/my-deployment"             -> Azure OpenAI
#   "anthropic/claude-sonnet-5"       -> Anthropic
#   "ollama/llama3.2"                 -> a model running on your laptop
#   "openai/my-model" + LLM_API_BASE  -> any OpenAI-compatible server (vLLM, LM Studio, ...)
MODEL = os.getenv("LLM_MODEL", "gpt-4.1-mini")
API_BASE = os.getenv("LLM_API_BASE")  # only needed for self-hosted / gateway endpoints
EXTRA_HEADERS = json.loads(os.getenv("LLM_EXTRA_HEADERS") or "{}")
# Context window override for models LiteLLM doesn't know (self-hosted, gateways).
MAX_INPUT_TOKENS = int(os.getenv("LLM_MAX_INPUT_TOKENS") or 0) or None

SYSTEM_PROMPT = os.getenv(
    "SYSTEM_PROMPT",
    "You are a helpful assistant. Be concise and concrete.",
)


def _build_messages(message: str, history: list[dict] | None = None) -> list[dict]:
    messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    messages.extend(history or [])
    messages.append({"role": "user", "content": message})
    return messages


def count_tokens(message: str, history: list[dict] | None = None) -> int:
    """Count the tokens a call to `stream_reply` would send, without sending it.

    Includes the system prompt and history. For models LiteLLM has no exact
    tokenizer for (self-hosted, most non-OpenAI), this is an estimate.
    """
    return token_counter(model=MODEL, messages=_build_messages(message, history))


def token_budget(message: str, history: list[dict] | None = None) -> dict:
    """Report how much of the model's context window a call would use.

    Returns {"used", "limit", "remaining"}. `limit` and `remaining` are None when
    the window size is unknown -- common for self-hosted models; set
    LLM_MAX_INPUT_TOKENS to supply it. `remaining` is the room left for the
    prompt, not the reply, and can go negative.
    """
    used = count_tokens(message, history)
    limit = MAX_INPUT_TOKENS
    if limit is None:
        try:
            limit = get_model_info(MODEL).get("max_input_tokens")
        except Exception:  # LiteLLM raises a bare Exception for unmapped models
            limit = None
    return {
        "used": used,
        "limit": limit,
        "remaining": None if limit is None else limit - used,
    }


def stream_reply(message: str, history: list[dict] | None = None):
    """Yield the assistant's reply as it arrives, one growing string at a time.

    `history` is a list of {"role": ..., "content": ...} dicts. We rebuild the
    full message list on every turn -- the model is stateless, so the
    conversation only exists because we keep sending it.
    """
    messages = _build_messages(message, history)

    kwargs = {"model": MODEL, "messages": messages, "stream": True}
    if API_BASE:
        kwargs["api_base"] = API_BASE
    if EXTRA_HEADERS:
        kwargs["extra_headers"] = EXTRA_HEADERS

    reply = ""
    for chunk in completion(**kwargs):
        piece = chunk.choices[0].delta.content
        if piece:
            reply += piece
            yield reply
