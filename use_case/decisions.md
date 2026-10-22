# Decision log

One row per architectural decision, with the option you rejected and why.

> **Week 5 asks you to defend your agent architecture against the alternatives.**
> **Week 10's handoff doc is largely this file.** Both are much easier if you
> wrote the reasoning down while you still remembered it.

A decision without a rejected alternative is not a decision, it is a default.
If you cannot name what you did not do, you did not choose.

| Week | Decision | What you rejected | Why | What would change your mind |
| --- | --- | --- | --- | --- |
| 1 | Two features: single incident and backfill | having just batch categorization | We need to be able to categorise individual incidents too, not run batch jobs every night. I would want the categorization to be immediate so that the user can see the results right away | If immediate categorization is deemed too expensive or is not used as often as I expected, it would make sense to just batch process on a defined cadence |
| 1 | Backfill logic should reuse the same categorization logic as single incident | For batch categorization to be its own separate piece of code | For the sake of logical simplicity and to avoid code duplication, I think it makes sense to loop over the single categorization logic for backfill | If backfill data is so huge that looping over single incidents becomes a performance bottleneck, I would consider a separate batch processing approach |
| 1 | single-incident classification is a function, not an agent (0 of 4) | single-incident classification is an agent | I chose to make single-incident classification a function because it is a simple, focused task that doesn't require the complexity of an agent. | If classification fails to keep human review under 25%, but the most of these issues were resolved by looking at past incidents, I would consider using an evidence fetching step and then compare it against this function as the baseline. |
| 1 | PRB matching is done by a code lookup after the model call, and that it's deferred | PRB matching is done by the model itself | I chose to make PRB matching a separate step after the model call because it is a simple, focused task that doesn't require the complexity of an agent. | If PRB matching fails to keep human review under 25%, I would consider using an evidence fetching step and then compare it against this function as the baseline. |
| 1 | LLM model is Ollama | LLM model is OpenAI | I chose to use Ollama because it is a local model that doesn't require an API key and can be run on my local machine. | If Ollama doesn't provide the required performance or accuracy, I would consider using OpenAI. |
| 1 | Thinking model needs a bigger context window | Thinking model runs with the default context window | I chose to use increase the model context window because the incidents can be quite long and I want to be able to fit as much context as possible in the model call. | If the model with a bigger context window doesn't provide the required performance or accuracy, I would consider using a model with a smaller context window. |
| 3 | <!-- retrieval approach --> | <!-- --> | <!-- --> | <!-- --> |
| 5 | <!-- agent architecture --> | <!-- --> | <!-- --> | <!-- --> |
| 6 | <!-- guardrail level --> | <!-- --> | <!-- --> | <!-- --> |
| 7 | <!-- memory type --> | <!-- --> | <!-- --> | <!-- --> |
| 8 | <!-- model --> | <!-- --> | <!-- --> | <!-- --> |

---

**Counter-argument (Week 1):** A single call only sees the incident in front of it. An agent that can look at a single incident and similar past incidents would likely categorize cases that currently require human review, which is exactly the review load we want to cut.

The last column is the one people skip and the one people ask about. "We chose
dense retrieval; we would switch to hybrid if exact-match queries went above ~20%
of traffic" is an engineering position. "We chose dense retrieval" is a
preference.
