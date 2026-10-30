# Project charter

<!--
  Fill this in during TC1 Step 4, from your Getting to Concreteness form.
  Later weeks' notebooks read this file and stop if it is still the template.
  That is on purpose.
-->

**Department:** Network Engineering

**Working title:** ToilMap: Problem Aggregation Agent

---

## The problem

**Who has it?** One real role, not a department.

Network reliability engineers and their team leads. Engineers feel the daily cost, and leadership bears the budget, risk, and capacity costs.

**What are they trying to do?**

Group recurring problems into categories, measure them, and decide what to automate first. Valuable evidence about what drives our toil already exists in resolved incidents, work notes, and PRBs, but it is scattered and unaggregated.

**How do they handle it today?**

Today the workflow is entirely manual and driven by individual memory. Engineers resolve each incident on its own, link it to a problem record (PRB) only when they happen to remember one, and decide what to automate in a monthly meeting where people share experiences. No step in the workflow systematically groups recurring incidents, measures their cost, or ranks them.

Ticket categories are broad and inconsistent, so counting by category hides the real causes. Two incidents with the same underlying trigger can be filed under different categories.

**What does that cost — time, money, risk, or relationships?**

The effort estimates in the form are about 3,900 engineer-hours a year, roughly 2.2 FTE: about 990 hours for manual grouping, review, and reporting, and about 2,900 hours for repeat incidents that the process never eliminates. Engineers resolve roughly 25 incidents a day, about 60% of which are recurrences; each recurrence costs an estimated 45 extra minutes of investigation.

If nothing changes, the repeat work grows with the service, and decisions about what to automate keep being made without evidence. The largest categories stay invisible.

**The problem in one sentence. No solution in it.**

The team can’t see which recurring problems cost the most effort, so the biggest sources of toil go unnamed and unautomated.

---

## Success

**What does the new world look like for that person?**

The agent takes over the slow, repetitive reading and grouping that nobody has time to do systematically, and engineers spend the time on building automation and fixing root causes instead. It reads every resolved incident and PRB, groups them into categories, measures each category, checks PRB coverage, and proposes a ranked list with evidence. Humans keep every decision.

It replaces the monthly opinion-sharing meeting with a report engineers can check, and it gives leadership a ranked list for deciding what to automate first.

**How would the firm measure it? Which numbers should move?**

- Manual grouping, PRB linking, review prep, and reporting: from about 990 to under about 310 engineer-hours a year, a reduction of about 70% (~680 hours).
- Repeat-incident toil: target a 30–40% reduction (~900–1,200 engineer-hours a year) once the top categories are automated. This depends on the team acting on the ranked list.
- Share of incidents linked to a PRB rises each quarter, and no recurring category stays without a PRB for more than a quarter.
- Time to answer "what are our top recurring issues?" drops from days to minutes.
- Prototype pass bar: measured on 400 synthetic Incidents with known correct outcomes:
  - **Auto-decisions are trustworthy:** at least 90% of incidents classified into a toil category can be trusted to be correct. The incidents that get tagged as non-toil can also be trusted.
  - **Auto-rejections are rarer mistakes still:** at least 95% of incidents classified as non-toil are found to be correctly classified. A wrongly classified incident creates more noise in the data as compared to an incident that was wrongly sent for human review.
  - **Every type of resolution works:** recall of at least 85% on each of the 10 toil categories. No single policy can be carried by the others.
  - **Review load actually drops:** no more than 25% of incidents are sent to human review, compared with 100% today. Without this ceiling, the first line can be met by sending everything to a person.
  - **Confidence means something:** among decisions made at 0.9 confidence or higher, the observed accuracy is within 5 points of the stated confidence.
  - **Better than doing nothing clever:** at least 20 points above a keyword-rule baseline on the auto-decision accuracy above.
  - **Zero writes:** the prototype never modifies any incident records.

The hour savings are targets based on the effort estimates in the form, not measurements. The prototype’s reviewer test is what would confirm them.

---

## The first product

**Your solution in one sentence.**

A problem aggregation agent for network reliability engineers and their team leads that uses resolved incidents, work notes, and existing problem records (PRBs) to produce a ranked, evidence-backed list of recurring toil categories with volume, hands-on hours, trend, and PRB gaps, helping them cut about 70% of the manual grouping and review work (~680 engineer-hours a year) and target a 30–40% reduction in repeat-incident toil (~900–1,200 hours a year).

**Input → Output.** Be specific enough that someone could build it wrong and you
would notice.

ToilMap has two features that share one classifier. **Single incident** classifies one new incident as it arrives. **Backfill** is a one-time batch over existing incidents. It loops the single-incident classifier, then adds deterministic rollups (counts, hours, trend) and a separate periodic PRB audit to produce the ranked toil report.

| | |
| --- | --- |
| **In: single incident** | Just the incident ID: `aggregate run --incident <id>`. Incident text and timestamp come from a lookup, and the taxonomy and PRBs are loaded server-side. Text is scrubbed (IPs, hostnames, tokens, names replaced with placeholders; responders hashed) before the model sees it. There is no `--domain` flag, because all synthetic data is network-domain. |
| **Out: single incident** | One structured record: suggested category, matched PRB ID (if any), `needs_human`, confidence (a 0-1 range), and a reason. There are exactly three types of outcomes, and the output schema should reject everything else. The MVP does not contain this feature (1) A confident category from the taxonomy. (2) `not_toil`: confident the incident is a one-off, no human needed. (3) new suggested category: `needs_human` must be true and the incident goes to a reviewer. A single incident reports only whether it matches an existing PRB. MERGE, SPLIT, and STALE are batch-level judgments and are not made here. |
| **In: backfill** | `aggregate run --since 2026-01-01`. For the smallest end-to-end prototype: about 400 synthetic incidents (268 confirmed incidents across ten hidden toil categories in uneven volumes, so the ranking has a known right answer; 40 noise incidents; 12 incidents whose cause fits no existing category; and 80 with no confirmed cause: 60 where none was found and 20 where the record leans toward one of several competing explanations without confirming it). The mix comes from published network-incident studies where they exist and is assumed elsewhere (see `decisions.md`, Week 2). Also 12 synthetic problem records (PRBs), `taxonomy.json`, and the team's own perceived top-10 toil list, read by a local command-line tool. |
| **Out: backfill** | A ranked toil report. Each category has incident count, hands-on hours, distinct responders, trend, an automatability score, PRB status, and three cited example incidents. PRB status (NO_PRB, MERGE, SPLIT, or STALE) comes from a separate periodic PRB audit over the whole batch. Also a CSV, a trend chart, draft PRB proposals that are never applied, and a comparison with the team's own top-10 list. A reviewer resolves every `needs_human` incident and accepts, merges, splits, renames, or rejects categories through a small review CLI. |
| **Taxonomy** | `taxonomy.json` holds 10 seed network categories plus `not_toil`. Hardware and Power/Environmental are separate categories, because the organization tracks them separately. Config/change-induced and human/process errors are merged into one Change-Induced Errors category. Humans own the taxonomy: when an incident fits nothing, a reviewer either assigns it to an existing category or approves a suggested category and adds it to the taxonomy.json file. The model proposes but never adds categories. |

The tool is read-only: it proposes changes, and engineers decide what to automate.

---

## Decisions made later

<!--
  Amended as the cohort goes. Keep the reasoning, not just the choice — Week 5
  asks you to defend your architecture against the options you rejected, and
  Week 10's handoff doc is largely this section.
-->

| Week | Decision | Why, and what you rejected |
| --- | --- | --- |
| 3 | Retrieval approach (provisional): hybrid embedding and keyword retrieval over scrubbed incidents, work notes, and PRBs, served through one read-only retrieval server (MCP), with a verifier pass | Free-text work notes describe the same cause in different words, so the agent starts from an embedding cluster, then expands it with differently worded queries, pulls nearby look-alikes to rule them out, and a verifier re-reads every cited incident before a label is accepted. Alert history and change records are optional later sources. Rejected: embedding-only clustering (misses incidents worded differently and cannot separate look-alikes); counting by ticket category (broad and inconsistent); a naive same-alert-within-7-days rule (kept only as the baseline the agent must beat); live ticketing integration for the MVP (read-only export instead). |
| 5 | Agent architecture (provisional): an orchestrator running four narrow subagents (normalizer, grouper and labeler, verifier, PRB auditor); read-only; counts, hours, and trends computed by deterministic code | Separate steps can be evaluated on their own, and the verifier is independent of the labeler so the agent does not grade its own work. A fixed budget (about 12 tool calls per category) applies, and unresolved items are marked "needs human review". Rejected: a single end-to-end agent (cannot tell which step failed, and it would check its own labels); autonomous PRB creation, linking, or remediation (excessive agency, and benchmarked agents were weaker at root cause analysis and mitigation than at grouping and localization); rules-only correlation (cannot read free-text work notes). Superseded for single incident by the Week 1 verdict in decisions.md; revisit in Week 5|
| 8 | Model: local open-source models through Ollama, nomic-embed-text for embeddings and llama3.1:8b for extraction and labeling | No incident text leaves the machine or network, which keeps the MVP clear of security review blockers. The tasks are narrow (schema extraction, labeling, rubric scoring) with strict JSON output, validated and retried once. A production model still needs security and AI-governance approval and must clear the eval pass bar. Rejected: hosted frontier models for the MVP (approval and privacy overhead before scrubbing is proven); revisit only if the local model misses the pass bar and the data is cleared. |