# Project charter

<!--
  Fill this in during TC1 Step 4, from your Getting to Concreteness form.
  Later weeks' notebooks read this file and stop if it is still the template.
  That is on purpose.
-->

**Department:** Network Engineering

**Working title:** ToilMap : Problem Aggregation Agent

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

- Target about a 70% reduction in manual grouping and review work (~680 engineer-hours a year).
- Target a 30–40% reduction in repeat-incident toil (~900–1,200 engineer-hours a year).
- Use the prototype’s reviewer test to assess time per review and the share of categories rated “real.”

The hour savings are targets based on the effort estimates in the form, not measurements. The prototype’s reviewer test is what would confirm them.

---

## The first product

**Your solution in one sentence.**

A problem aggregation agent for network reliability engineers and their team leads that uses resolved incidents, work notes, and existing problem records (PRBs) to produce a ranked, evidence-backed list of recurring toil categories with volume, hands-on hours, trend, and PRB gaps, helping them cut about 70% of the manual grouping and review work (~680 engineer-hours a year) and target a 30–40% reduction in repeat-incident toil (~900–1,200 hours a year).

**Input → Output.** Be specific enough that someone could build it wrong and you
would notice.

| | |
| --- | --- |
| **In** | For the smallest end-to-end prototype: 240 synthetic resolved incidents and 12 synthetic problem records (PRBs), read by a local command-line tool. The example invocation selects a domain, a start date, a PRB path, and a minimum cluster size. |
| **Out** | A ranked toil report. Each category has volume, hands-on hours, trend, an automatability score, PRB coverage, and cited example incidents. A reviewer accepts, merges, splits, or rejects each category through a small review CLI. The tool is read-only: it proposes changes, and engineers decide what to automate. |

---

## Decisions made later

<!--
  Amended as the cohort goes. Keep the reasoning, not just the choice — Week 5
  asks you to defend your architecture against the options you rejected, and
  Week 10's handoff doc is largely this section.
-->

| Week | Decision | Why, and what you rejected |
| --- | --- | --- |
| 3 | Retrieval approach | <!-- TC3 --> |
| 5 | Agent architecture | <!-- TC5 --> |
| 8 | Model | <!-- TC8 --> |
