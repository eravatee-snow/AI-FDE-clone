import asyncio
import sys
import time

from fastmcp.server.middleware import Middleware

from classifier import classify_incident
from incidents import get_incident
from utcp import call_with_utcp, call_with_utcp_batch

# GS-01 (clear toil), GS-02 (not_toil), GS-05 (unclassified): three different paths through the rules
INCIDENTS = ["INC-0001", "INC-0002", "INC-0005"]


class Meter:
    """Counts model round trips and the tokens they cost."""

    def __init__(self):
        self.calls = 0
        self.tokens = 0
        self.first_turn_tool_calls = None

    def track(self, response):
        self.calls += 1
        usage = getattr(response, "usage", None)
        if usage:
            self.tokens += usage.total_tokens or 0
        choice = response.choices[0]
        tool_calls = [(c.function.name, c.function.arguments) for c in (choice.message.tool_calls or [])]
        if self.calls == 1:
            self.first_turn_tool_calls = len(tool_calls)
        print(f"  round {self.calls}: finish_reason={choice.finish_reason} "
              f"tokens={getattr(usage, 'total_tokens', None)} tool_calls={tool_calls}")
        print(f"    text: {(choice.message.content or '')[:400]!r}", flush=True)

class CapabilityCounter(Middleware):
    """Counts the calls that reach one tool on a server, under any namespace."""

    def __init__(self, tool_name: str):
        self.tool_name = tool_name
        self.calls = 0

    async def on_call_tool(self, context, call_next):
        if context.message.name.endswith(self.tool_name):
            self.calls += 1
        return await call_next(context)


class CountingLookup:
    """The baseline has no MCP layer, so count by wrapping the function it calls."""

    def __init__(self, lookup):
        self.lookup = lookup
        self.calls = 0

    def __call__(self, incident_id):
        self.calls += 1
        return self.lookup(incident_id)


def report(label, meter, counter, started):
    print(f"{label}: model calls {meter.calls}, get_incident calls {counter.calls}, "
          f"seconds {time.perf_counter() - started:.1f}, tokens {meter.tokens}, "
          f"first-turn tool calls {meter.first_turn_tool_calls}", flush=True)


def run_baseline(ids, label):
    meter, counter = Meter(), CountingLookup(get_incident)
    started = time.perf_counter()
    for incident_id in ids:
        print(classify_incident(incident_id, lookup=counter, meter=meter).model_dump_json())
    report(label, meter, counter, started)


async def run_utcp(ids, label):
    # One counter across every call: each call builds its own server, the middleware object is shared
    meter, counter = Meter(), CapabilityCounter("get_incident")
    started = time.perf_counter()
    for incident_id in ids:
        print(await call_with_utcp(incident_id, meter, counter))
    report(label, meter, counter, started)


async def run_utcp_batch(ids, label):
    meter, counter = Meter(), CapabilityCounter("get_incident")
    started = time.perf_counter()
    print(await call_with_utcp_batch(ids, meter, counter))
    report(label, meter, counter, started)


async def main():
    """Usage: python test.py [--single] [--several] [--batch] [--utcp-only]. Default is --single."""
    args = set(sys.argv[1:])
    several = "--several" in args
    batch = "--batch" in args
    utcp_only = "--utcp-only" in args

    if not (several or batch) or "--single" in args:
        if not utcp_only:
            print("Baseline, single...", flush=True)
            run_baseline(INCIDENTS[:1], "Baseline, single")
        print("UTCP, single...", flush=True)
        await run_utcp(INCIDENTS[:1], "UTCP, single")

    if several:
        if not utcp_only:
            print(f"Baseline, several {INCIDENTS}...", flush=True)
            run_baseline(INCIDENTS, "Baseline, several")
        print(f"UTCP, several (code loop) {INCIDENTS}...", flush=True)
        await run_utcp(INCIDENTS, "UTCP, several (code loop)")

    if batch:
        print(f"UTCP, one conversation {INCIDENTS}...", flush=True)
        await run_utcp_batch(INCIDENTS, "UTCP, one conversation")

if __name__ == "__main__":
    asyncio.run(main())
