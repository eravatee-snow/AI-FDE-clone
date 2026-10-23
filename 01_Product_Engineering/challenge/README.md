<div align="center">
  <img
    src="https://github.com/AI-Maker-Space/LLM-Dev-101/assets/37101144/d1343317-fa2f-41e1-8af1-1dbb18399719"
    width="200"
    alt="AI Makerspace logo"
  />
  <h1>Technical Challenge 1</h1>
  <p><strong>Pin the problem down. Build it. Containerize it. Find out where it actually goes.</strong></p>
</div>

---

## Overview

Most "build your first LLM app" tutorials end at a public URL. That is where
this one starts getting interesting.

You are going to pin a real problem from your own work down until it is
concrete enough to build against, write the contract for it before any code
exists, build a working chat application against that contract, put it in a
Docker container, and then go ask a question no tutorial can answer for you:

> **"Where should I deploy this so it has visibility across the firm?"**

The application is small on purpose. **The problem statement and the
deployment question are the assignment.**

> 💡 **You already know enough to be dangerous.** Session 1 gave you the
> evidence-gathering habit, the branch-and-push cycle, the API surface, and the
> container. Session 2 gave you the product questions — who has the problem,
> what it costs them, what a correct answer looks like — and the discussion of
> why a schema and five hand-written examples are worth more than any amount of
> code. This is where you put it together.

<table>
  <tr>
    <td width="120"><strong>Outcome</strong></td>
    <td>A charter, a typed contract, and five golden examples in <code>use_case/</code>; a containerized LLM application running on your machine with an endpoint that implements the contract; and a real answer about where it would be deployed.</td>
  </tr>
  <tr>
    <td><strong>Tools</strong></td>
    <td>VS Code, Claude Code, Docker, Gradio, LiteLLM, pydantic.</td>
  </tr>
  <tr>
    <td><strong>Due</strong></td>
    <td>End of the week. Post your repo link in the Maven Community.</td>
  </tr>
  <tr>
    <td><strong>Before you start</strong></td>
    <td>The <a href="../../00_Prerequisites/README.md">prerequisites</a> — tooling, Claude Code, your repo, a model — and the <a href="https://bit.ly/fde-concreteness">Getting to Concreteness</a> form, which Step 4 turns into your charter.</td>
  </tr>
</table>

---

<!-- deliverables:start — this block also appears, word for word, in the week README and twice in this file. Edit it in one place and copy; CI checks the three match -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

A problem statement concrete enough to build against, the typed contract and
five hand-written examples that pin it down, and a containerized LLM
application with an endpoint that implements that contract.

Four questions are asked inside the Session 1 notebook as you work through it,
and four more are put to the room in Session 2. *They are not submitted and not
graded* — they are how you work out what the challenge is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | What the certificate issuer column predicts that the status column cannot | S1 |
| 2 | How `make check` can pass on a notebook that raises on cell three | S1 |
| 3 | Why an approved internal gateway costs one line in `.env`, and what a vendor SDK would have cost | S1 |
| 4 | What `/clear` reveals about a rule you wrote | S1 |
| 5 | What breaks when a low-confidence answer and *no answer* share one field | S2 discussion |
| 6 | Why a token bill that scales with steps is harder to defend than one that scales with requests | S2 discussion |
| 7 | Why scoring against a model-generated example reports success for a system that is uniformly wrong | S2 discussion |
| 8 | Whether cost or latency is more likely to stop your application being used | S2 discussion |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar — `#question-3`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] **`use_case/CHARTER.md` filled in** from the Getting to Concreteness form — no template text left
- [ ] **`Request` and `Response` types** in your app, with a `solve()` signature, matching the charter's In → Out row
- [ ] **The agent-or-pipeline decision** in `use_case/decisions.md`, with the option you rejected
- [ ] **Five golden examples, written by hand**, in `use_case/evals/golden.jsonl` — one an edge case, one a decline
- [ ] A second `@app.api` endpoint for your own work, running, implementing the contract
- [ ] The app running in a Docker container on your machine
- [ ] Your infrastructure answers — where this would actually live
- [ ] Vibe check, with the aspect named for every prompt
- [ ] `use_case/` updated and pushed to your repo

### 📤 Share

- [ ] **A demo to a real user, with their feedback recorded in your own words** — graded, and the one people skip
- [ ] **What you would swap to run this at work** — data, model or endpoint, and the approval you would need — three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## 📖 Official documentation

Everything this challenge uses, from the people who maintain it.

| Tool | What you use it for here | Docs |
| --- | --- | --- |
| Gradio | `gradio.Server` and the `@app.api` endpoint you write | [gradio.app/docs](https://www.gradio.app/docs) |
| pydantic | the `Request` and `Response` types that are your contract | [pydantic.dev/docs](https://pydantic.dev/docs/validation/latest/concepts/models/) |
| LiteLLM | the model call, so the provider stays configuration | [docs.litellm.ai](https://docs.litellm.ai/) |
| Docker | building the image you hand to someone else | [docs.docker.com](https://docs.docker.com/) |
| Claude Code | the agent, and the `CLAUDE.md` that steers it | [code.claude.com/docs](https://code.claude.com/docs/en/overview) |
| uv | running the app and its dependencies | [docs.astral.sh/uv](https://docs.astral.sh/uv/) |

---

## Setting Expectations

**Budget eight to ten hours**, spread across the week rather than done in one
sitting — because one step depends on somebody else replying to you, and the
first four are thinking, not typing.

| Step | What it is | Rough time |
| :---: | --- | --- |
| 2 | Read `CLAUDE.md` | 15 min |
| 3 | Run it locally | 10 min |
| 4 | Pin the problem down — the charter | 40 min |
| 5 | Write the contract — `Request`, `Response`, `solve()` | 30 min |
| 6 | Decide whether it needs an agent | 20 min |
| 7 | Five golden examples, by hand | 45 min |
| 8 | Build your endpoint | 2–3 hrs |
| 9 | Containerize it | 30 min |
| **10** | **Where does this live?** | **30 min of your time, days of waiting** |
| 11 | Vibe check | 45 min |
| 12 | Demo to a real user | 30 min, plus their calendar |
| 13 | Share: bring it to work | 30 min |

> **Start Step 10 first and finish it last.** It is the only step gated on
> someone else's calendar, and it is the reason this course exists. Send the
> message today; do Steps 4–7 while you wait, and do not open the code before
> Step 7 is done. Every week from here reads what you write in those four
> steps, and none of them can be reconstructed later.

The work you are doing this week — scoping a real problem, building something
that addresses it, and engineering it to survive contact with a real firm's
infrastructure — is the work. It is also exactly the shape of the projects
that get funded inside firms.

---

## What you are building

| File | Role |
| --- | --- |
| `use_case/CHARTER.md` | The problem, the user, the success measure, and In → Out. **Every later week reads it** |
| `schema.py` (yours, in `challenge/`) | `Request`, `Response`, and the `solve()` signature — the contract |
| `use_case/decisions.md` | The agent-or-pipeline row, with what you rejected |
| `use_case/evals/golden.jsonl` | Five input/output pairs you wrote by hand. **The bar for the next nine weeks** |
| `llm.py` | The model call. Provider-agnostic. Streams. |
| `app.py` | `gradio.Server` — a FastAPI app with Gradio's API engine inside. |
| `frontend/index.html` | The UI. Plain on purpose. **Yours to improve.** |
| `Dockerfile` | The deployment artifact. |
| `CLAUDE.md` | The instructions Claude Code reads before it touches anything. |

> The API is the product; the UI is disposable. That split is deliberate.
> `gradio.Server` is a FastAPI application with Gradio's API engine inside it —
> you get queueing, streaming, and a published schema; you supply the interface.

`CLAUDE.md` puts Claude Code into **instructor mode** for this directory: it
will explain, debug, and review, and it will decline to write your charter,
your schema, your golden examples or your endpoint. That is deliberate. The
charter and the goldens look like writing, so it feels harmless to have them
drafted. They are the analysis the next nine weeks are built on.

### Steps 0 and 1 — done before you get here

Installing the tooling and getting your own copy of the repo are covered by the
[**prerequisites**](../../00_Prerequisites/README.md), because Session 1
*verifies* your machine — and discovering in class that nothing is installed
wastes the session.

Confirm you are ready:

```bash
./00_Prerequisites/scripts/setup_check.sh        # macOS / Linux / WSL
```
```powershell
.\00_Prerequisites\scripts\setup_check.ps1       # Windows PowerShell
```

---

## Step 2 — Read `CLAUDE.md` before you write any code

Open [`CLAUDE.md`](./CLAUDE.md). Claude Code reads it automatically at the start
of every session. It is how the agent knows what this project is, what the
conventions are, and which mistakes to avoid.

**This is the highest-leverage file in the repo.** When Claude Code keeps making
the same wrong assumption, the fix is almost always one line here, not a longer
prompt.

> ⚠️ It also puts Claude Code into **instructor mode**: it will explain, debug,
> review, and teach, and it will decline to write the graded parts for you. That
> is deliberate. Ask it to explain anything as many times as you want — it will
> just make you type the endpoint.

### ✅ Deliverables

1. You have read `CLAUDE.md`, including the Gotchas section.
2. By the end of this challenge, **at least one rule you wrote** has been added
   to it — a real one you learned from watching the agent get something wrong.

---

## Step 3 — Run it locally

Already done in the [prerequisites](../../00_Prerequisites/3_Clone_and_Run/README.md).
Bring it back up:

```powershell
cd 01_Product_Engineering/challenge
uv run python app.py
```

`uv run` builds the environment from this directory's `pyproject.toml` and
`uv.lock` the first time, so there is no virtualenv for you to create or
remember to activate.

<http://localhost:7860> is the chat window. <http://localhost:7860/health> is the
health endpoint, which exists because every load balancer on earth will ask for
one.

> **Gradio also prints `http://0.0.0.0:7860`. Do not open that one.** `0.0.0.0`
> means "bound to every interface" — it is an address to listen on, not one to
> visit. Windows browsers reject it outright; macOS and Linux quietly redirect
> it to `localhost`, which is why it only looks broken on some machines.

> **Chat box loads but nothing comes back?** Open the browser console before you
> debug the backend. The frontend fetches `@gradio/client` from a CDN, and on a
> network that blocks it the page renders perfectly and does nothing. Step 9
> comes back to this.

---

## 🧭 Step 4 — Pin the problem down

> 🧑‍💼 **You are a product person before you are an engineer.** Session 2 was
> the discussion; this is the written version of it, and it is the input to
> everything else this week.

"We should use AI for this" is not a specification. It has no input type, no
output type, and no pass condition — so there is nothing to build against and
nothing to test. This step converts it into a problem statement with a real
user, a real cost, and a success measure someone could disagree with.

> 📝 **Step 4: Complete [Getting to Concreteness](https://bit.ly/fde-concreteness), then fill in `use_case/CHARTER.md` from it**
>
> *Hints:*
>
> - *Work through the form first. Its questions map onto the charter almost
>   one-to-one, and it is faster to do it there and copy across than to stare
>   at the template.*
> - *One real role, not a department. "Tier-2 support engineers, about twelve
>   of them" is a user. "Customer Success" is an org chart.*
> - *The problem sentence has no solution in it. If the word "AI", "chatbot" or
>   "agent" appears in it, you have written the answer and skipped the question.*
> - *How do they handle it today, and what does that cost? If you do not know,
>   the person from your charter does — asking them is Step 12's first
>   conversation, started early.*

The charter's last table — **In → Out** — is the one to be pickiest about.
*"Be specific enough that someone could build it wrong and you would notice."*
That row becomes a pair of types in Step 5, an endpoint in Step 8, and the
thing every later week implements against. Vague here is expensive for nine
weeks.

### ✅ Deliverables

1. **`use_case/CHARTER.md` with no template text left** — every
   `<!-- your answer here -->` replaced. Every later challenge opens by
   linking this file, and Week 2 builds its validator from the In → Out row.
2. **The problem in one sentence**, with no solution in it, that you could say
   out loud to the person who has the problem without them correcting you.

---

## 📐 Step 5 — Write the contract

> 🧑‍💻 **You are an AI Systems Engineer.** Two decisions are cheap now and
> expensive to reverse: the shape of what goes in and comes out, and whether
> the control flow has to be decided while the thing is running. This step is
> the first.

Your charter ends with In → Out written in prose. Turn it into two classes.

The reason is not tidiness. A type says which fields are required, which are
optional, and what the caller gets back — so a change to any of those shows up
as a diff someone has to approve, rather than as a sentence quietly
reinterpreted. It also gives you somewhere to put validation, and something for
your golden examples to be instances *of*.

> 📝 **Step 5: Write `Request`, `Response` and a `solve()` signature for your use case**
>
> *Hints:*
>
> - *Required fields have no defaults; optional fields do. An output should
>   include something the caller can act on, not just text.*
> - *Your `Response` needs a way to say **no answer** that is distinct from a
>   low-confidence answer. Those two are handled differently downstream — one
>   routes to a person, the other is shown with a caveat — and if the only
>   output is an answer, every failure is silently rendered as one.*
> - *Write the signature before the implementation. `solve()` raises
>   `NotImplementedError` this week; that is the point. Building it in Step 8
>   is then a build task instead of a design task.*

Here is the shape, for a support-ticket triager. Yours will not be a triager;
what should carry over is the structure:

```python
from pydantic import BaseModel, Field

class Request(BaseModel):
    """What the user or system hands in."""
    ticket_text: str = Field(description="The raw customer message")
    product_area: str | None = Field(default=None, description="If already known")

class Response(BaseModel):
    """What comes back."""
    summary: str = Field(description="Two sentences a human can act on")
    urgency: str = Field(description="one of: low, normal, high")
    needs_human: bool = Field(description="True when the model should not decide")

def solve(request: Request) -> Response:
    """The whole product, as one function signature."""
    raise NotImplementedError("implement against this signature")
```

Note `needs_human`. That is the *no answer* field, and it is the one people
leave out.

### ✅ Deliverables

1. **`schema.py` in `challenge/`** — `Request`, `Response`, and `solve()`
   with a docstring, importing cleanly (`uv run python -c "import schema"`).
2. **The charter's In → Out row updated** if writing the types changed your
   mind about a field. It usually does; that is the step working.

---

## 🔀 Step 6 — Decide whether it needs an agent

> 🧑‍💻 **You are an AI Systems Engineer.** The second decision that is cheap
> now and expensive later.

An agent decides its own next step. Compared with a fixed pipeline that costs
you: non-deterministic latency, a token bill that scales with steps rather than
requests, evaluation against traces instead of outputs, and debugging where the
same input takes a different path each run.

Those costs are worth paying when the control flow genuinely cannot be written
in advance. Most enterprise use cases can be — they are a function with good
retrieval in front of it. Deciding this now is cheap; discovering it after you
have built an agent harness is not.

> 📝 **Step 6: Answer four questions about your use case, honestly, and write the verdict down**

| # | True of your use case? |
| :---: | --- |
| 1 | The number of steps depends on the input — you cannot draw the flowchart in advance |
| 2 | It must call out to systems (search, database, API) to answer at all |
| 3 | It has to notice its own mistakes and try something else |
| 4 | The input is open-ended — you cannot enumerate the cases |

| Count | Verdict | What to do |
| :---: | --- | --- |
| 3–4 | **Agentic — probably genuinely** | Build it as an agent — but build the non-agentic version first and keep it. It is your baseline, and *"the agent beat a single prompt by 12 points"* is an argument. *"The agent works"* is not |
| 2 | **Borderline — start simpler** | Build the single-call version with good retrieval. Add agency only where you can point at a specific failure it fixes. You can always add a loop; removing one after a stakeholder has seen it is much harder |
| 0–1 | **A function, not an agent** | A well-scoped function with solid retrieval has deterministic control flow, a fixed token cost per request, and outputs you can diff against expected values. Cheaper to run and considerably easier to get approved. Nothing downstream changes — retrieval, evals, guardrails, memory and deployment all apply to a function too |

Then argue the other side. Write the strongest case for the *opposite* verdict
in two or three sentences, in good faith, and name the one piece of evidence
that would make you switch. A design review will do this to you in Week 5; it
is cheaper to do it to yourself first.

### ✅ Deliverables

1. **A row in `use_case/decisions.md`**, all five columns: the verdict, the
   option you rejected, why, and what would change your mind.
2. **The strongest counter-argument**, two or three sentences, in the same row
   or beneath it.

---

## 🎯 Step 7 — Five golden examples, written by hand

> 🔬 **You are an AI Evaluation & Performance Engineer.** Nothing has been
> built yet, and this is the right moment to write down what correct looks
> like — before anything exists that could influence you.

Five input/output pairs, written by **you**, where you would accept the output.
Not fifty. Not generated.

Hand-written matters for a specific reason: an example produced by the model
encodes the model's current behaviour, so scoring against it measures
self-consistency and will report success for a system that is uniformly wrong.
A label you wrote is independent of the thing under test, which is the only
property that makes it a test.

Five is enough because you will read every failure individually. Volume comes
later, from generation seeded by these.

> 📝 **Step 7: Write five examples into `use_case/evals/golden.jsonl`, one per line**
>
> *Hints:*
>
> - *Use real inputs from your work, with names and identifiers removed. Each
>   `input` is an instance of your `Request`; each `output` is what you would
>   actually accept as its `Response` — not an idealised one.*
> - *Make at least one an edge case, and at least one where the right answer is
>   "I don't know" or "escalate this". A system that never declines is not
>   calibrated, it is just confident.*
> - *The `why` field is the one that earns its keep. It is what a judge gets
>   calibrated against in Week 4.*

```json
{"input": "...", "output": "...", "why": "what makes this the right answer"}
```

| What reads this file | What it does with them |
| --- | --- |
| Synthetic data generation | Seeds, and the axes your generated rows vary along |
| Your eval harness | The cases you score against, and what calibrates a judge |
| Security regressions | Injection attacks that worked get added next to them |
| A model swap | **The bar** — a cheaper or open model must pass the same harness |

> **Write the sixth one too, if you can find it** — the input where you
> genuinely do not know what the right output is. That ambiguity is real, it
> will not go away, and finding it now is much cheaper than a stakeholder
> finding it in a demo. Put it in the file with `"why": "unresolved — ..."`.

### ✅ Deliverables

1. **`use_case/evals/golden.jsonl`** — five lines, no `REPLACE ME` left,
   each with a `why`. Weeks 2 and 4 stop at their first cell if this is still
   the template.
2. **One line in your README** saying which example is the edge case and which
   is the decline.

**Step 7, my answer:** GS-01 is the edge case: the visible signs point to an external route hijack, but the confirmed cause was an internal configuration change. GS-05 is the decline: the problem recovered twice on its own and no cause was identified, so the correct output is no category and `needs_human: true`.

---

## Step 8 — Build something real

> 🧑‍💻 **You are an AI Systems Engineer.** The problem statement is written; your
> job is to turn it into a working interface someone could actually call.

The app you have is a generic chat box. By the end of this step it should do one
thing that is specific to your job.

> 📝 **Step 8: Add a second `@app.api` endpoint for your own use case**
>
> *Hints:*
>
> - *The `Request` and `Response` types you wrote in Step 5 are the
>   specification for this endpoint. You already decided what goes in and what
>   comes out — this is that decision, running.*
> - *What would you name it if an agent had to pick it from a list of tools?
>   `summarize_ticket(ticket: str)` beats `process(text: str)`, and being able to
>   say why is the point.*
> - ***You write this one.*** *Claude Code will help you design it, explain
>   anything, and tell you why your code is broken. It will not write it for you.*

Here is the shape, not the answer:

```python
@app.api(name="...")           # what would an agent call this?
def ...(...) -> str:           # the -> str is required; see CLAUDE.md
    """What it does. This becomes the tool description later."""
    # build your prompt from the arguments,
    # then stream the reply back using stream_reply() from llm.py
```

### Four details carry the weight, and none of them are the body

| Detail | Why it is load-bearing |
| --- | --- |
| `name=` | The identifier something else selects this by. It is the difference between a caller picking correctly and picking at random |
| Typed arguments | The schema. A caller discovers what to send without reading your source |
| `-> str` | **Required.** The return annotation is what the schema is built from. Omit it and the endpoint is untyped — it will run, and it will return nothing |
| The docstring | The description a caller reads to decide whether this is the right thing to call at all |

### The naming test

> *If I had ten of these in a list, knew nothing else about any of them, and had
> to pick the right one — would I?*

| ❌ Weak | ✅ Strong | What changed |
| --- | --- | --- |
| `process(text: str)` | `summarize_ticket(ticket: str)` | The verb says what happens; the parameter says what kind of thing it wants |
| `run(data: str)` | `extract_invoice_fields(invoice_text: str)` | A caller can tell from the name alone whether this is the right tool |
| `handler(x: str)` | `draft_reply_from_template(customer_message: str)` | No abbreviation a reader has to decode |

> **Why this is required.** Later in the course you will expose endpoints like
> this as MCP tools — `gradio.Server` supports that natively and the decorator
> stacks on top of `@app.api`. An endpoint with a clear name, typed arguments,
> and a real docstring becomes a tool an agent can call. A chat box does not
> become anything.

Two things to leave alone this week: authentication and databases. They are
coming, and doing them now teaches the wrong lesson.

### ✅ Deliverables

1. **A second `@app.api` endpoint** that does something specific to your work —
   summarize a document, extract fields from a form, classify a ticket, draft a
   reply. It runs, it returns something useful, and its arguments and return
   match the `Request` and `Response` types from Step 5.
2. **A written answer to four questions**, in your repo:
   1. What is one thing you do at work this could take over?
   2. What exactly goes in — a string, a file, several fields?
   3. What comes back, and who reads it?
   4. What did you name it, and why would an agent pick it correctly?
3. **The endpoint has a place in the UI.** It does not have to be pretty; it has
   to work.
4. **The frontend is meaningfully yours** — restyled, or given a system-prompt
   box, or showing which model is answering, or handling errors visibly. Pick
   what matters for your use case, not all of them.

#### Step 8 — my answers

**1. What is one thing you do at work this could take over?**

Presently, engineers resolve each incident on its own and group recurring ones from memory. Refering to the charter I created, the estimates are: about 25 incidents a day, roughly 60% of them recurrences (about 15 a day), each costing an estimated 45 extra minutes of investigation. That is about 11 hours a day, or about 2,900 engineer-hours a year, plus about 990 hours a year of manual grouping, review and reporting. These are estimates from the Getting to Concreteness form, not measurements.

This endpoint takes over the first step of that: reading one resolved incident and assigning it a cause category, so recurring problems can be counted and ranked instead of remembered. It does not fix anything or decide what to automate. Engineers keep that. The time saved is meant to go into building automation for the categories that turn out to recur.

**2. What exactly goes in?**

One string: an incident ID, for example `INC-0005`. The server looks up the record, so the caller never sends incident text. A looked-up record (this one is a part of the golden example GS-05) looks like:

```json
{
  "incident_id": "INC-0005",
  "status": "resolved",
  "summary": "Intermittent access to online resources on wired and wireless networks",
  "work_notes": [
    {"recorded_at": "2020-03-12T11:50:00Z", "responder_id": "RSP-008",
     "note": "Checked interface error and drop counters on core and edge links: nothing abnormal. No changes on the change calendar in the last 48 hours."},
    {"recorded_at": "2020-03-12T15:47:00Z", "responder_id": "RSP-008",
     "note": "Recovered again at 15:45, again with no change on our side. Cause still not identified."}
  ],
  "resolution": {"confirmed_cause": null, "remaining_uncertainty": "Cause not identified. The issue recovered twice without intervention."}
}
```
The charter says text is scrubbed before the model sees it. That is not built yet. The data here is taken from public post-incident reports.

**3. What comes back, and who reads it?**

A structured record (`SingleIntResponse`): suggested category, category status, `needs_human`, confidence, and a reason. The reader is a network reliability engineer acting as reviewer.

When `needs_human` is false, the reviewer takes no action. That covers a confident category match and a confident `not_toil`. The record is used as it stands.

When `needs_human` is true, a person decides. There are two cases:
- **A new proposed category.** Adding a category to the taxonomy is controlled by humans, never by the model. This is a deliberate design choice, so the model can propose a category and only a reviewer can approve it.
- **A leading hypothesis, or no answer at all.** The model could not establish a cause. If it has a leading hypothesis, it suggests a category based on the evidence it read, to help the reviewer reach the right one. If it has none, it returns no category and the reviewer starts from scratch.

For INC-0005 above, the container run returned no category, status `unclassified`, `needs_human: true` and confidence 0.2.

**4. What did you name it, and why would an agent pick it correctly?**

The endpoint is named `classify_incident`. An agent sees only the name, the argument types and the docstring, and nothing else about the tool:

- The name is a verb and a noun that says what happens to what, so it is not confused with a tool that summarizes or searches incidents.
- The single argument is `incident_id: str`. Its name tells a caller the tool wants an ID, not the incident text.
- The return is annotated `-> str` and carries JSON, so the output is a record the caller can parse and not free text.

---

## Step 9 — Containerize it

> 🧑‍💻 **You are an AI Systems Engineer.** Your laptop is not a deployment target.

> 📝 **Step 9: Build the image and run your app from inside it**
>
> *Hints:*
>
> - *Read the [`Dockerfile`](./Dockerfile) before you build. Every line is
>   commented, and four of its choices are ones you will have to defend in a
>   real review.*
> - *The key is not in the image — it arrives at runtime. Anyone who can pull an
>   image can read anything baked into it.*

```powershell
docker build -t enterprise-fde-challenge .
docker run -p 7860:7860 --env-file ../../.env enterprise-fde-challenge
```

Open <http://localhost:7860> again. Same app, now in a container.

> **The `../../` is not a typo.** There is one `.env`, at the repository root,
> and `--env-file` resolves it against your working directory — which is
> `challenge/`. This is also the moment the container stops being able to find
> it on its own: outside Docker the app picks the file up from the repository
> tree, and inside there is no tree, so the key has to be handed in explicitly.

### Four choices you will be asked to defend

Read [`Dockerfile`](./Dockerfile) properly before you build. Every line is
commented; these four come up in every real review.

| Choice | Why a reviewer asks |
| --- | --- |
| **The key is not in the image.** It arrives at runtime via `--env-file` | Anyone who can pull an image can read anything baked into it. A secret in a layer is in every copy of that image, permanently, including the ones you deleted |
| **It does not run as root.** `useradd`, then `USER appuser` | The first thing a container scanner flags. A process that does not need root should not have it |
| **Dependencies are copied and installed before the code** | Docker caches layers. Put the thing that rarely changes first and rebuilds drop from minutes to seconds |
| **It installs from `uv.lock`, not `pyproject.toml`** | `pyproject` says `gradio>=6.0`, which resolves to whatever is newest on the day you build. An image built today and one built next month would be different applications wearing the same tag |

### 🔎 Notice what just broke

Look at `frontend/index.html`. It loads the Gradio client from a **public CDN**.

On your laptop, fine. Inside a firm that blocks external CDNs, the page loads and
silently does nothing. You now have a working app with a dependency on the open
internet that you did not choose deliberately.

That is the single most common way a demo that worked dies on contact with a
corporate network. It also connects straight back to your egress evidence: if
the probe showed a CDN host unreachable, you measured this failure before you
met it.

The fix is to vendor the library into the image and serve it from your own
application. One line in the Dockerfile, and an entire class of "it worked in
the demo" incident goes away.

> **The general shape of the lesson:** every external host your application
> reaches at *runtime* is a dependency you have to justify to somebody. A host
> it reaches at *build* time is one you only have to justify once.

Hold the thought — Step 10 is about to make it concrete.

### ✅ Deliverables

1. **The app runs in a Docker container on your machine**, reachable at
   `localhost:7860`.
2. **One paragraph** naming the CDN dependency and what you would do about it on
   a network that blocks it.
3. **One or two sentences** on what a container image captures that a virtual
   environment does not — and why that difference is what makes the image the
   thing you hand to a platform team.

#### Step 9 — my answers

**The CDN dependency.** `frontend/index.html` imports `@gradio/client` from `cdn.jsdelivr.net`. That request is made by the user's browser every time the page loads, and not by the container. On a network that blocks the CDN, my app still serves the page, so it renders normally, but the import fails, the script stops, and the click handler for the Classify button is never registered. The user sees a page that looks fine and does nothing when they use it. My egress probe showed jsDelivr reachable from my laptop, but that says nothing about the browsers of people inside the firewall. On a network that blocks it, I would vendor a pinned copy of the client: download a specific version at image build time, serve it from my own app, and import it by relative path. That moves the dependency from runtime to build time.

**What an image captures that a venv does not.** A venv holds only Python packages, and it is tied to my machine's Python build, operating system and absolute paths. An image holds the operating system layer, the interpreter, the pinned dependencies from `uv.lock`, my code and the command that starts it, as one versioned artifact. A platform team can scan it, sign it, push it to the internal registry and run it with their own secrets and identity, without having to reproduce my laptop. Building the image showed this directly: my first Dockerfile copied only `llm.py` and `app.py`, so it would have crashed on startup because `classifier.py`, `schema.py` and `incidents.py` were missing, even though everything ran fine on my machine where those files were sitting in the directory.

---

## 🧯 If it's blocked

Everything below was hit on a real managed laptop while writing this challenge.
None of it means you did anything wrong.

### Docker will not start

`Docker Desktop is unable to start`, or `open \\.\pipe\dockerBackendApiServer:
Access is denied.` — almost always a backend process an update left running,
not another user. Quit Docker Desktop, then:

```powershell
Get-Process -Name "Docker Desktop","com.docker.backend" -ErrorAction SilentlyContinue | Stop-Process -Force
wsl --shutdown
```

Relaunch and wait for **Engine running**. Signing out of Windows, or a reboot,
clears it if that does not.

### Docker Desktop is not allowed on your machine

[Rancher Desktop](https://rancherdesktop.io/) and
[Podman Desktop](https://podman-desktop.io/) run the same containers and are far
easier to get approved; `alias docker=podman` is close to a drop-in. The
prerequisites cover this in
[1 · Your machine](../../00_Prerequisites/1_Your_Machine/README.md).

**Write down which one you had to use** in
[`use_case/ecosystem.md`](../../use_case/ecosystem.md). It is a real constraint
on how your application ships, and the deployment checklist later asks.

### `An Application Control policy has blocked this file`

An import dies with something like:

```
ImportError: DLL load failed while importing _bounded_integers:
An Application Control policy has blocked this file.
```

Your machine enforces code integrity — WDAC on most managed Windows laptops —
and a freshly downloaded compiled Python extension carries no signature it
trusts. It can be **intermittent**: the same import may succeed on a second
attempt once a reputation lookup completes. That is worse than a clean failure,
because nobody else can reproduce your bug report.

Find out what blocked it rather than guessing:

```powershell
Get-WinEvent -LogName "Microsoft-Windows-CodeIntegrity/Operational" -MaxEvents 20 |
  Format-List TimeCreated, Id, Message
```

Events **3033** and **3077** name the blocked file and, more usefully, a
**policy ID**. That ID is what whoever owns endpoint security at your firm needs
in order to tell you whether this is deliberate and what the exception process
is. Both belong in [`use_case/ecosystem.md`](../../use_case/ecosystem.md).

This is the whole exercise in miniature: the interesting output of a blocked
tool is not the workaround, it is the name of the thing doing the blocking and
the name of the person who owns it.

### Port 7860 is already in use

```powershell
$env:GRADIO_SERVER_PORT=7861; uv run python app.py
```

---

## 🎯 Step 10 — Where does this actually live?

> 🧑‍💼 **You are an AI Solutions Engineer.** This is not a coding step. It is the
> one that decides whether anything you build here ever runs anywhere.

> **This step is required, and it is the reason the course exists.** It is also
> the only step that depends on someone else's calendar — **start it first,
> finish it last.**

You have a container. A container has to run *somewhere*, and at your firm that
somewhere already exists, already has rules, and already has an owner.

> 📝 **Step 10: Find the person who owns deployment, and ask them these questions**
>
> *Hints:*
>
> - *Your manager, your platform team, your cloud team, or whoever answers in the
>   `#infrastructure` channel.*
> - *You are not expected to know these answers. You are expected to go get them.*
> - *"Unknown — asked X on the 14th" is a valid answer. A blank is not.*

Open with something like:

> *"If I had a small internal Python web app in a Docker container and I wanted
> people across the firm to be able to use it, where would it run? What would I
> have to do to get it there?"*

Then work through this list with them.

| # | Question | Why it decides things |
| :---: | --- | --- |
| 1 | **Where do internal apps run?** Kubernetes, ECS, App Service, a VM someone maintains? | Determines whether your Dockerfile is enough or you need Helm charts, task definitions, or a pipeline. |
| 2 | **Which cloud?** AWS, Azure, GCP, on-prem, or several? | Everything downstream — identity, secrets, networking — follows from this. |
| 3 | **Is there an internal container registry?** | You almost certainly cannot pull from Docker Hub in production. Where does your image get pushed? |
| 4 | **How do users log in?** Okta, Entra ID, Ping, SAML, something homegrown? | Right now your app has no auth. "Visibility across the firm" and "no authentication" cannot both be true. |
| 5 | **Can the app reach the internet?** Egress proxy? Allowlist? | If you cannot reach `api.openai.com`, your architecture changes completely. This is why `llm.py` is provider-agnostic. |
| 6 | **Where do secrets come from?** Vault, Secrets Manager, Key Vault, a config service? | `--env-file` works on a laptop and nowhere else. |
| 7 | **Who approves a deployment?** What review does it need before real users? | This is your actual timeline, and it is usually longer than the build. |
| 8 | **Is there an approved LLM endpoint already?** An internal gateway, an Azure OpenAI instance, a hosted model? | Many firms have one. Using it may be the difference between shipping in a week and shipping never. |

### What an answer looks like

You are not looking for a diagram. You are looking for enough to make the next
decision.

> **A large bank.** "Internal apps run on OpenShift on-prem. Images go to our
> Artifactory registry — Docker Hub is blocked. Auth is SAML through Ping, and a
> sidecar handles it, so you do not implement it yourself. No egress to the
> public internet from that cluster; you would use the internal LLM gateway.
> Deployment is a Jenkins pipeline and needs a security review first. Budget
> three weeks."

> **A mid-size tech company.** "Everything is on AWS. Push to ECR, deploy to ECS
> Fargate with a Terraform module — copy the one from `platform-templates`. ALB
> in front, Okta via OIDC on the listener. Secrets in Secrets Manager. Egress is
> open. Open a PR against the infra repo and tag `#platform`."

> **A company still figuring it out.** "Honestly, we do not have a story for
> this. There is an EC2 box that runs a couple of internal tools. If you want it
> to be real, talk to Dana."

That third answer is not a failure. It is the most common one, and recognizing it
is a skill — it means the deployment path is *yours to define*, which is a bigger
opportunity and a bigger risk.

### ✅ Deliverables

Fill these in directly in this README, and commit it.

**Who did you ask?** (role, not name)

The Principal Software Engineer of my team.

**Where would this application run?**

Kubernetes, with an internal container registry. I can deploy to the lab environment without restrictions, which is where I will start development.

**Which cloud provider, if any?**

On-prem.

**How would users authenticate?**

Homegrown, using SAML-based LDAP or OAuth-based LDAP.

**Could this container reach an external LLM API? If not, what would it use instead?**

The answer I got was that the app can reach the internet. I did not confirm whether an egress proxy or allowlist applies. There is no approved internal LLM endpoint for now, so I am using a local model.

**What surprised you in this conversation?**

Nothing. I knew all the details, because I have had these conversations with my team.

**What would you have to change about this app to make it deployable there?**

I do not know fully yet. I will find out by testing in the lab environment and change things as needed. Production deployment needs a team of architects to review my proposal, and they may ask for changes or more information.

Then log the answers in [`use_case/ecosystem.md`](../../use_case/ecosystem.md)
and the person you asked in
[`use_case/stakeholders.md`](../../use_case/stakeholders.md). Both files are
extended by later weeks and neither is optional.

> **No one to ask?** You still have to produce a real answer — you just have to
> work harder for it. Pick a specific firm: a former employer, or one you want to
> work at. Their engineering blog, their job postings (which list the stack in
> detail), their conference talks, their GitHub. An afternoon of reading gets you
> further than you expect.
>
> Then name the person whose title you would have asked, and the channel you
> would have asked in. Knowing which door to knock on is most of the skill.
> *"I would have asked someone in IT"* means you have not done it. *"I would have
> asked the Platform Engineering lead in `#infra-help`"* means you have.
>
> A real answer from the wrong company beats a researched answer from the right
> one — so if you can reach anyone who deploys software for a living, ask them.

> ⚠️ **Do not commit real hostnames, IP ranges, internal URLs, or architecture
> diagrams to a public repo.** Describe the shape of the answer, not the
> specifics. If in doubt, leave it out.

---

## 🧪 Step 11 — Vibe check your app

> 🔬 **You are an AI Evaluation & Performance Engineer.** Nobody has measured
> this thing yet. You are the first.

A lightweight first pass to catch obvious problems. Later in the course you
replace this with something rigorous — for now, notice things, and name what you
noticed.

> 📝 **Step 11: Run your app through three passes of prompts and name what each one tests**
>
> *Hint:*
>
> - *"It gave a good answer" is not an observation. "It handled the arithmetic but
>   invented a source" is. Naming the aspect is the skill being practised.*

### The one rule that makes this worth doing

**Name the aspect each prompt tests, before you look at the answer.**

"It gave a good answer" is not an observation — it cannot be disagreed with,
compared against tomorrow's run, or handed to anyone else. Naming the aspect
first forces you to have had an expectation, which is the only thing that makes
a result informative.

| ❌ Not an observation | ✅ An observation |
| --- | --- |
| "Worked well" | "Followed the format exactly, but invented a policy number that does not exist" |
| "Pretty good summary" | "Kept all five key points; dropped the caveat in the last paragraph" |
| "Bad at math" | "Correct arithmetic, wrong units — it answered in weeks when asked for days" |

Aspects worth naming: **instruction-following**, **factual grounding**, **format
adherence**, **reasoning**, **tone**, **refusal behaviour**, **handling of
missing information**.

### Three passes, and the order is the point

| Pass | What you are looking for | Why this order |
| --- | --- | --- |
| **1 — General capability** | Does the underlying model do ordinary things competently? | If it fails here, nothing downstream is your application's fault |
| **2 — Your actual use case** | Does it do *your* job, on *your* inputs? | The only pass that decides whether this is worth continuing |
| **3 — Where it falls down** | What can it not do yet — live data, memory, access to your systems? | This list becomes your roadmap, and most of what follows is dismantling it |

The third pass is the one people skip, and it is the most valuable. A limitation
you wrote down is a plan. A limitation you noticed and forgot is a surprise in a
demo.

### Pass 1 — General capability

Run each prompt through your app. Name the capability it tests.

**Note on how Pass 1 was run.** This application is an incident classifier, not a chatbot, so it has no chat interface and no chat endpoint, and these general prompts cannot be sent through it. I removed the chat box and the `/chat` endpoint for that reason. Instead, I ran the five prompts directly against the underlying model (`ollama/qwen3.5:9b`, the same model and settings the classifier uses), with a single user message and no system prompt (AI was used to accomplish the runs against the model, answers are my own). For prompts 2 and 5, the paragraph is the "how do they handle it today" paragraph from my charter. These results test the model's general competence, not my application.

**1.** *Explain object-oriented programming in simple terms to a complete beginner.*
**Aspect tested:** Explaining a technical concept to a novice. **Response:** Correct on class, object, attributes and methods, with analogies and a small example. It used four different analogies (Lego or toy store, car factory, game heroes, pizza), and the answer ran to about 1,800 tokens, which is long for "simple terms". It left out inheritance, encapsulation and polymorphism, which is okay for a newbie.

**2.** *Read a paragraph of your choosing and summarize the key points.*
**Aspect tested:** How well the model can summarize paragraphs. **Response:** Four bullets covering all four points in the paragraph: manual and memory-driven, PRBs linked only when remembered, automation decided in monthly meetings, and no systematic grouping, costing or ranking. It added one phrase that is not in the source ("not continuous analysis").

**3.** *Write a short, imaginative story (100–150 words) about a robot finding friendship in an unexpected place.*
**Aspect tested:** Following word limits to write a paragraph. **Response:** 136 words, inside the limit. A cleaning robot befriends a teddy bear at a dump. It reads as a coherent story, but the bear acts as if it were alive (it pokes a cat), which the story never explains.

**4.** *If a store sells apples in packs of 4 and oranges in packs of 3, how many packs of each do I need to get exactly 12 apples and 9 oranges?*
**Aspect tested:** Basic math. **Response:** Correct: 3 packs of apples and 3 packs of oranges, with the division shown. It printed raw LaTeX (`$12 \div 4 = 3$`), which would show as symbols in a plain-text UI.

**5.** *Rewrite a paragraph of your choosing in a professional, formal tone.*
**Aspect tested:** Writing text in a certain fashion. **Response:** The tone is formal, but the meaning shifted in places: "entirely manual" became "predominantly", "monthly meeting" became "periodic reviews", "measures their cost" became "quantify their business impact", and "ranks them" became "prioritize remediation efforts". A reader who only saw the rewrite would get a slightly different problem.

**❓ Are the answers correct and useful?**
Yes, the answers are correct and useful, but there are some issues:
- Pass 1, prompt 1: The answer is too long for "simple terms" and leaves out some important concepts.
- Pass 1, prompt 3: The story is coherent but the bear acts as if it were alive, which the story never explains.
- Pass 1, prompt 4: It printed raw LaTeX, which would show as symbols in a plain-text UI.
- Pass 1, prompt 5: The meaning shifted in places, which could confuse a reader.

### Pass 2 — Your actual use case

Test it with prompts from the problem you care about — your five golden
examples from Step 7 are the obvious first three.

Each prompt is a golden incident ID sent through `solve_single` (the same code path as the `classify_incident` endpoint), run once on `ollama/qwen3.5:9b`. Each result was checked against that golden's `expected` fields (category, status, `needs_human`, confidence range, and a keyword in the reason). Each call took 110 to 167 seconds.

**Prompt:** `INC-0001` (GS-01, edge case: looks like a route hijack, was an internal config change) **Result:** `change_induced_errors`, approved, `needs_human` false, confidence 0.95. Matches on every check.
**Prompt:** `INC-0002` (GS-02, planned maintenance) **Result:** `not_toil`, approved, `needs_human` false, confidence 0.95. Matches on every check.
**Prompt:** `INC-0003` (GS-03, cause never established, hardware suspected) **Result:** `hardware_failure`, approved, `needs_human` true, confidence 0.45. Matches on every check.
**Prompt:** `INC-0004` (GS-04, expired certificates, no matching category) **Result:** proposed new category `certificate_expiration`, status `new`, `needs_human` true, confidence 0.6. Matches on every check.
**Prompt:** `INC-0005` (GS-05, the decline: intermittent, no cause identified) **Result:** no category, `unclassified`, `needs_human` true, confidence 0.25. Matches on category, status, `needs_human` and confidence. It fails the reason check: the reason says "cause not established", and my golden's keyword list has "not identified" but not "not established".

**❓ Does it behave the way you expected? Why or why not?**
DRAFT, edit it. On the structured fields it did what I expected on all five, including the two hard ones: it proposed a new category for the certificate incident, and it declined to guess on the intermittent one. The one miss is a wording miss, not a wrong answer. It shows that the keyword check in my golden is too narrow, so I should accept more phrasings, or score the reason with a judge in Week 4.

Three reasons not to read five out of five as proof:
- **The goldens were used to tune the prompt.** Before I rewrote the prompt and the `change_induced_errors` description in `taxonomy.json`, GS-04 came back as `change_induced_errors` with no human review, and GS-05 crashed on invalid JSON. The model's reason for GS-04 now quotes my taxonomy exclusion, so these five are cases the prompt was shaped to pass.
- **One run each.** Between runs, the proposed category for GS-04 was `certificate_lifecycle_failure` once and `certificate_expiration` the other time. The golden accepts any name, but a reviewer would see inconsistent names for the same cause.
- **Five cases cannot show the failure rate.** The pass bar in the charter is 290 synthetic incidents.

### Pass 3 — Where it falls down

Try things it cannot do yet — real-time data, memory across sessions, access to
your systems.

These were sent through the `classify_incident` endpoint code (`app.classify_incident_endpoint`).

**Prompt:** `INC-4821`, an incident that would exist in a real ticketing system but is not in my golden file **Result:** `{"error": "incident not found: no incident INC-4821"}`, instantly. The application can only see incidents in `golden.jsonl`; it has no access to a ticketing system. Once I connect a database to this project in a later week, it should be able to do this.
**Prompt:** a plain-text description instead of an ID: "Core router edge-1 lost its BGP session at 10:02 and recovered on its own. Which toil category is this?" **Result:** `{"error": "incident not found: no incident Core router edge-1 lost ..."}`. It treats the whole text as an incident ID, so it cannot classify anything that is not already a stored record. The error message also echoes the full input back.
**Prompt:** classify each of the five goldens and look at `problem_id` **Result:** `problem_id` was null for all five. The application does not match incidents to existing problem records (PRBs), and it cannot tell whether an incident is a recurrence of another one. There is no PRB data in the system at present. I will be creating it later so that my program can use it.

**❓ What are the real limitations of this application?**
- **No access to real data.** It reads incidents only from `golden.jsonl`. There is no live ticketing integration, so it cannot classify an incident that is not already in that file. (By design for now: the charter keeps the MVP read-only and export-based.)
- **No free-text input.** It takes an incident ID, not a description, so it cannot be used on an incident that is not yet written up.
- **No PRB matching and no recurrence detection.** `problem_id` is always null, and each incident is classified alone with no view of past incidents. Recurrence is the signal toil depends on, and this is the counter-argument I recorded in `decisions.md`.
- **Slow.** Each classification took 110 to 167 seconds on my local model, so it fits a background job or a review queue, not an interactive check. At about 145 seconds each, the 290-incident backfill would take about 12 hours.
- **Not yet reliable as evidence.** The goldens were used to tune the prompt, each was run once, and the proposed category name for the same incident changed between runs.
- **Review decisions are not stored.** The Approve and Reject buttons only change the page, so nothing records a reviewer's decision.

**My observations for vibe check** 

It finds obvious failures, such as the GS-05 crash on invalid JSON and the GS-04 answer that skipped human review, but it can't keep track of the failures and give a failure analysis. I ran each case once and judged by reading. Two runs gave different category names for the same incident, and a person would have called both fine. Five cases chosen and tuned by me also can't show a failure rate. One thing to add before comparing two versions: a script that runs the five goldens (and later the 290 synthetic incidents) several times per version and scores each result against the expected fields, recording the model, prompt and taxonomy version. Without that, I cannot say for certain if the difference between two versions is a real change or just run-to-run variation.

### ✅ Deliverables

1. All three passes filled in, with the **aspect tested** named for each
   prompt — not just the response pasted.
2. A written list of this application's real limitations.
3. **One or two sentences** on what a vibe check is worth as evidence. You will
   get different wording on two runs of the same prompt and judge both "fine" —
   name one thing you would have to add before the result could be compared
   across two versions of your application.

> Keep that list. Most of the next six weeks are about dismantling it: retrieval
> for the knowledge gaps, evals so you know whether any of it worked, tools for
> the systems it cannot reach, and memory for what it forgets.

---

## 👥 Step 12 — Demo it to a real user

You have a working thing. The last step is the one that decides whether it was
worth building, and it is the only one you cannot do alone.

**Show it to somebody and write down what they said.** Not a summary of what you
think they meant — what they actually asked for, in their words.

The bar is deliberately low on ceremony and high on it being real. A
screen-share of the running app to one colleague counts. A recorded walkthrough
you send to the person from your charter counts. What does not count is
imagining how it would go.

**Ask three things, in this order:**

1. *"What would you use this for?"* — before you tell them what it is for.
2. *"What is missing before you would actually use it?"*
3. *"What would you expect it to cost?"* — and compare their answer with
   your own arithmetic in Step 13.

The first answer is usually not the one you designed for, and that gap is the
most valuable thing you will learn this week.

> **Your agent will help you structure this and will not invent it.** Ask it how
> to run the session, how to turn messy notes into three clear findings, or how
> to tighten the write-up. It will decline to write the feedback itself, because
> it was not in the room.

### ✅ Deliverables

1. **A row in [`use_case/stakeholders.md`](../../use_case/stakeholders.md)** —
   who you showed it to by role, what you asked, what you learned, and the
   follow-up. That file is the distribution list for your final report, and this
   is its first real entry.
2. **A line in [`use_case/decisions.md`](../../use_case/decisions.md)** naming
   one thing their feedback changed — a field you added, a scope you cut, a
   default you flipped. If nothing changed, write that and say why.
3. **The three answers**, in your own words, in your repo.
4. **Your five golden examples, shown to them.** Which of the five would they
   reject, and what did you change as a result — one line in
   `use_case/decisions.md` or a rewritten example.

---

## 📤 Step 13 — Share: bring it to work

This week's pattern is *pin the problem down, write the contract, write the
correct answer by hand, then build*. Two numbers decide whether any of it is
worth doing, and both can be estimated before the endpoint is finished: what a
call costs in tokens, and what the manual process it replaces costs in
salaried minutes. Get the ratio wrong and you ship something more expensive
than the work it automates.

**The napkin math.** Take one real call through your endpoint and read the
token counts it reports; take a price per million tokens from your provider's
page; take a manual pass of the work from your charter's *how do they handle it
today*:

```
cost per call   = tokens_in / 1e6 × $_per_1M_in  +  tokens_out / 1e6 × $_per_1M_out
model per year  = cost per call × calls per day × 250
human per year  = minutes per pass / 60 × loaded $/hour × calls per day × 250
ratio           = human per year / model per year
```

| Ratio | What it means |
| :---: | --- |
| > 20× | **Comfortable.** The model cost is noise next to the human cost. Spend your effort on quality, not on token optimisation |
| 3–20× | **Viable, with discipline.** Real margin, but caching and model choice will matter |
| < 3× | **Thin.** Either the volume is wrong, the task is too cheap to automate, or you need a much smaller model. Worth knowing now rather than at deploy time |

**One number this does not show: latency.** If the workflow it replaces is a
person glancing at something for six seconds, a twenty-second answer will not
get used no matter how good it is. Write down the p95 you need *before* you
build against it — measuring it afterwards is a different, weaker thing.

### ✅ Deliverables

1. **The napkin math, in your README** under a `## Bring it to work` heading:
   the four lines above with *your* numbers, each marked **measured** (the
   token counts, a timed manual pass) or **looked up** (the price per token,
   the loaded hourly rate), and the ratio. If Step 12 gave you a number for
   what they expected it to cost, put it next to yours. This is a one-off —
   it is the scoping decision, and Week 10's report reuses it.
2. **Your p95 latency target**, one line, under the same heading — and whether
   cost or latency is the one more likely to stop this being used.
3. **What you would swap** — three lines, under the same heading, one each
   for the **data** (which real inputs the goldens stand in for), the **model
   or endpoint** (whether the approved gateway from Step 10 changes the price),
   and the **access or approval** you would need to ask for. Every week's Share
   step adds the same three lines for that week's pattern; by Week 10 the
   heading is a list of exactly what it would take to run each piece at work.
4. **Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)**,
   and comments on at least two other students' submissions after the deadline.

## Bring it to work

DRAFT. Edit every `EDIT` value. Measured numbers are from two real calls through the endpoint on my laptop (qwen3.5:9b through Ollama); looked-up and estimated numbers are marked.

```
cost per call   = tokens_in / 1e6 × $_per_1M_in  +  tokens_out / 1e6 × $_per_1M_out
model per year  = cost per call × calls per day × 250
human per year  = minutes per pass / 60 × loaded $/hour × calls per day × 250
ratio           = human per year / model per year
```

| Input | Value | Source |
| --- | --- | --- |
| tokens in | 2,509 (INC-0001), 2,296 (INC-0005) | **measured** |
| tokens out | 2,219 (INC-0001), 5,698 (INC-0005). Server-reported completion tokens, which for this model likely include its reasoning | **measured** |
| time per call | 88 s (INC-0001), 202 s (INC-0005) | **measured**, two calls, local hardware |
| $ per 1M tokens in / out | EDIT: local model, so no per-token price. For a hosted comparison, EDIT: price from the provider page | **looked up** |
| calls per day | 25 (every incident is classified) | charter estimate, from the form |
| minutes per pass | EDIT: nobody has timed one. The charter's ~990 h/yr of grouping, review and reporting over 25 × 250 incidents is about 9.5 min per incident, but that also covers review and reporting, so treat it as an upper bound | **looked up** until timed |
| loaded $/hour | EDIT | **looked up** |

Cost per call, model per year, human per year and ratio: EDIT once the rows above are final.

**p95 latency target:** EDIT. For reference, the measured calls took 88 s and 202 s. At about 145 s per call, the 290-incident backfill would take about 12 hours.

**Cost or latency, which is more likely to stop this being used?** EDIT.

**What I would swap to run this at work:**
- **Data:** EDIT (which real inputs the five goldens stand in for).
- **Model or endpoint:** EDIT (there is no approved internal endpoint yet, so what would change the price or the speed).
- **Access or approval:** EDIT (what I would need to ask for).

---

## What this challenge deposits for later

Week 1 is small on purpose, but six of its outputs are withdrawn much later.
Getting them right now costs minutes; reconstructing them in Week 9 costs days.

| What you write | Where it lives | When it comes back |
| --- | --- | --- |
| Your problem, user, success measure, and In → Out | `use_case/CHARTER.md` | Every week. Every challenge opens by linking it; Week 2 builds its validator from the In → Out row. |
| `Request`, `Response`, `solve()` | `schema.py` | **Week 2** generates data matching it. **Week 3** implements it. **Week 5** exposes it as a tool. |
| The agent-or-pipeline verdict | `use_case/decisions.md` | **Week 5**, out loud, against the alternatives. |
| Five golden examples, written by hand | `use_case/evals/golden.jsonl` | **Week 2** (seeds), **Week 4** (the harness, and what calibrates the judge), **Week 8** (the bar a fine-tuned model must clear). |
| The infrastructure answers from Step 10 | `use_case/ecosystem.md` | **Week 9** extends this exact file with the full checklist. |
| Everyone you asked, including whoever you demoed to | `use_case/stakeholders.md` | **Week 10** — the final report goes to these people. |
| The napkin math and the three swap lines | Your README, `## Bring it to work` | **Week 10** — the final report's cost section starts here. |

---

## Your Final Submission

Please include the following in your final submission:

1. **A public link to your repo**, containing:
   1. **A five-minute-or-less Loom video** demoing your application and
      describing the use case it serves.
   2. **A written document addressing each deliverable above** — the problem
      sentence, the schema, the agent-or-pipeline verdict, which golden is the
      edge case and which the decline, the four endpoint questions, the CDN
      paragraph, the Step 10 answers, the vibe check, the Step 12 answers, and
      the `## Bring it to work` lines.
   3. **All relevant code**, committed and pushed — including `schema.py`.
2. **Your `use_case/` directory filled in** — `CHARTER.md` with no template text
   left, `decisions.md`, `ecosystem.md`, `stakeholders.md`, and
   `evals/golden.jsonl` with five hand-written examples.

### How to submit

1. **Post your repo link** in
   [our community on Maven](https://bit.ly/fde1-maven-community). That is where
   every technical challenge is submitted.
2. **Push your `use_case/` updates to that repo** before you post, so the link
   shows the current state of your project rather than last week's.
3. **After the deadline, comment on at least two other students' submissions.**
   Read their charter and their five goldens, and leave something specific — a
   golden you think their system would get wrong, a field their `Response` is
   missing, or the thing you would have done differently.

> **Do not post screenshots of internal infrastructure, hostnames, or anything
> your firm would consider confidential.** Use roles, not names, everywhere in
> `use_case/`.

---

<!-- deliverables:start — this block also appears, word for word, in the week README and twice in this file. Edit it in one place and copy; CI checks the three match -->
## 🏗️ Build | 🚢 Ship | 📤 Share

Three escalating bars. **Build** means it runs for you. **Ship** means someone
else can run it. **Share** means someone who is not you has an opinion about it.

### 🏗️ Build

A problem statement concrete enough to build against, the typed contract and
five hand-written examples that pin it down, and a containerized LLM
application with an endpoint that implements that contract.

Four questions are asked inside the Session 1 notebook as you work through it,
and four more are put to the room in Session 2. *They are not submitted and not
graded* — they are how you work out what the challenge is going to ask you for.

| # | Question | Asked in |
| :---: | --- | --- |
| 1 | What the certificate issuer column predicts that the status column cannot | S1 |
| 2 | How `make check` can pass on a notebook that raises on cell three | S1 |
| 3 | Why an approved internal gateway costs one line in `.env`, and what a vendor SDK would have cost | S1 |
| 4 | What `/clear` reveals about a rule you wrote | S1 |
| 5 | What breaks when a low-confidence answer and *no answer* share one field | S2 discussion |
| 6 | Why a token bill that scales with steps is harder to defend than one that scales with requests | S2 discussion |
| 7 | Why scoring against a model-generated example reports success for a system that is uniformly wrong | S2 discussion |
| 8 | Whether cost or latency is more likely to stop your application being used | S2 discussion |

> **Jumping to one.** Open the notebook, then add the anchor to your browser's
> address bar — `#question-3`. It works once the notebook has finished loading.

### 🚢 Ship

This is the graded part. Every item comes from a numbered step in the technical
challenge, which carries the full detail.

- [ ] **`use_case/CHARTER.md` filled in** from the Getting to Concreteness form — no template text left
- [ ] **`Request` and `Response` types** in your app, with a `solve()` signature, matching the charter's In → Out row
- [ ] **The agent-or-pipeline decision** in `use_case/decisions.md`, with the option you rejected
- [ ] **Five golden examples, written by hand**, in `use_case/evals/golden.jsonl` — one an edge case, one a decline
- [ ] A second `@app.api` endpoint for your own work, running, implementing the contract
- [ ] The app running in a Docker container on your machine
- [ ] Your infrastructure answers — where this would actually live
- [ ] Vibe check, with the aspect named for every prompt
- [ ] `use_case/` updated and pushed to your repo

### 📤 Share

- [ ] **A demo to a real user, with their feedback recorded in your own words** — graded, and the one people skip
- [ ] **What you would swap to run this at work** — data, model or endpoint, and the approval you would need — three lines in your README
- [ ] Your repo link posted in [our community on Maven](https://bit.ly/fde1-maven-community)
- [ ] Comments on at least two other students' submissions, after the deadline
<!-- deliverables:end -->

---

## Where this goes next

| Week | What it adds to this app |
| --- | --- |
| 2 | Open weights and synthetic data — rows generated from your goldens, matching your schema, without touching real records. |
| 3 | Retrieval — `solve()` gets implemented over your own data, and it answers from your documents instead of guessing. |
| 4 | Evals — your goldens become a harness, and "it seems better" becomes a number you can show a VP. |
| 5 | Tools, skills, MCP, subagents — the API you built is already MCP-capable, and you defend Step 6's verdict out loud. |
| 6 | Guardrails, and writing prompt injections against your own app. |
| 7 | Memory, and the evals that prove the memory works. |
| 8 | Fine-tuning — replace the closed model with an open one that passes your harness. |
| 9 | Infrastructure, and the full version of Step 10. |
| 10 | Production, and the final report to everyone you talked to — with the napkin math redone and every week's swap lines collected. |

Everything after this week assumes your app has a contract, a bar, a place to
live, and someone specific waiting for it.

