# Datasheet

<!-- Written in TC2, alongside your synthetic data. This file is committed; the
     data itself is not. -->

## What this data is

**Generated on:** 2026-10-28 (pilots), 2026-10-29 (full run), 2026-10-30 (reprocess and top-up)
**Generated from:** the JSON shape of the five hand-written goldens in `use_case/evals/golden.jsonl` (themselves written from public RCAs, not company records) and the written axis descriptions in `02_Open_Weights/challenge/axes.py`. No real records.
**Rows:** 400, every label group exactly at its quota: 377 from the full run (prompt v1) and 23 from two top-ups (prompt v2). 15 rows were removed after reading (see *Leakage check*); a further 119 are set aside for reading and 73 held as surplus.

## Generation run

<!-- Filled in after Step 2. Enough for someone else to reproduce the run. -->

| Setting | Value |
| --- | --- |
| Model | `ollama/qwen3.5:9b` (9.7B, nvfp4) through Ollama's MLX runner, on an Apple M3 Pro with 18 GB, 100% GPU |
| Temperature | 1, the model's default (not overridden) |
| Top-p | 0.95, the model's default (not overridden). Also defaults: top-k 20, presence penalty 1.5 |
| Thinking | Off (`think: False`). On, it spent about 75% of output tokens on hidden reasoning |
| Context window | 16,384 tokens |
| Dedupe threshold | 0.7, character 4-gram Jaccard over summary, symptoms, work notes and resolution text |
| Rows per combination | 3 per call |
| Seeds shown to the generator | All five, GS-01 to GS-05 in file order, on every call |
| Prompt | v1: `helpers/sdg.py`'s `GENERATION_PROMPT` unchanged (full run). v2: the same with every category name and description added above it (top-up). Each row records its version as `_prompt_version`; rows without it are v1 |
| Sampling | By quota per label group (see *How the category is chosen*): 229 calls over 189 of the 408 live combinations, in 3 rounds, `SEED = 2`, sized for 60% of rows surviving. Top-up: 11 calls for the three short groups (`new_category` 7 rows, `link_circuit_carrier` 7, `routing_bgp` 4), `SEED = 3` so it would not repeat the full run's combinations |
| Second top-up | After the not_toil wording changed and 15 rows were removed: 3 calls for `not_toil` (4 rows short), 6 rows generated (3 lines unparseable), all 6 schema-valid, 1 set aside |
| Speed | Full run 104 s per call, 6.6 hours; first top-up 96 s per call, 17.6 minutes; second top-up 118 s per call, 5.9 minutes |

| Count | Full run | Top-up |
| --- | --- | --- |
| Generated | 591 parsed rows; a further 95 lines were unparseable | 31; 2 lines unparseable |
| After dedupe | 591 (0 dropped within rounds, 0 across rounds) | 31 (0 duplicates of each other or of existing rows) |
| Schema-valid | 585. This checks the incident only; the expected block is replaced from the axes afterwards | 31 |
| Dead combinations | 24 of 432: `misleading_ddos` × `security` and `misleading_dns` × `dns`, 12 each | same |

### After generation

Every schema-valid row then went through these steps:

1. **Relabelled from the axes.** `expected` is set by `expected_from_axes()` in `axes.py`, not taken from the model. The model's own guess is kept as `_model_expected`. Two fields the axes cannot decide come from the model: `reason_must_mention_any`, and the invented name for a new category. A new-category row with no usable snake_case name is dropped.
   - **IDs assigned by code.** Every row gets a unique `id` (`SYN-0001` onward) and `incident_id` (`INC-SYN-0001`). The model continued the goldens' numbering, so before this only 79 of 382 incident IDs were distinct (`INC-0006` appeared 108 times).
   - **Dangling links cleared.** `existing_links.incident_ids` and `problem_ids` are emptied on every row: 48 rows had links, copied in the goldens' style, to incidents and PRBs that do not exist. PRBs are created and assigned in a later step. `change_ids` are kept.
   - **Rows removed after reading.** The rows listed under *Leakage check* are kept out of every output file (`REMOVED` in `generate.py`) and written to `synthetic_v1.removed.jsonl` with their reasons.
2. **`must_not` guarded.** The tempting category (misleading rows) and the opposite of `needs_human` are added if missing; entries naming a category that does not exist, or contradicting the row's own label, are removed. Full run: 390 entries added, 489 removed.
3. **Set aside when the model disagrees.** Rows whose `_model_expected` disagrees with the axes label go to `synthetic_v1.review.jsonl`, not the dataset. The rule differs by evidence:
   - conflicting rows: set aside only if the model's `needs_human` differs, i.e. it judged the cause settled;
   - every other row: set aside if `needs_human`, `category_status` or the category differ. For v1 rows only, a category name outside the taxonomy counts as agreement when the model also marked it `approved`.
4. **Trimmed to quota.** Each group keeps at most its quota; the rest go to `synthetic_v1.surplus.jsonl`.

**The step 3 rule was loosened after seeing what it removed, and that is recorded here on purpose.** The first version set aside 306 of 577 rows; 206 of those used a category name that does not exist (`vendor_defect`, `bandwidth_saturation`, `facility_event`), because the v1 prompt never showed the model the taxonomy. Those disagreements measured the model's vocabulary, not whether the incident fit its axes. The looser rule applies to v1 rows only; v2 rows are held to the real names. The same pass tightened the new-category name check after 7 of 12 names turned out to be a description copied from GS-04.

| After generation | Original rule | After reprocess | After first top-up | After removal and second top-up (final) |
| --- | --- | --- | --- | --- |
| Dropped: new category with no usable name | 8 | 15 | 15 | 15 |
| Removed after reading | — | — | — | 15 |
| Set aside for reading | 306 | 116 | 118 (2 of the 31 v2 rows, under the strict rule) | 119 |
| Surplus | 34 | 72 | 83 | 73 |
| In the dataset | 237 | 382 | 400 | 400 |

## Variation axes

<!-- Must match 02_Open_Weights/challenge/axes.py: same axes, same values. -->

| Axis | What real variation it covers | Values | What it drives in the expected output |
| --- | --- | --- | --- |
| evidence | How much of what the engineers knew made it into the record, and so how settled the cause is. Covers lossy notes and knowledge that never left the engineer | `complete`, `partial`, `conflicting`, `absent` | Whether the cause is established: an auto-decided category (complete, partial), a leading hypothesis sent for review (conflicting), or no category (absent) |
| surface_vs_cause | Whether the first visible symptoms point at the real cause or at a tempting wrong one | `direct`, `misleading_ddos` (looks like `security`), `misleading_dns` (looks like `dns`) | A misleading row never expects the tempting category, and its `must_not` always forbids it |
| outcome_type | The hidden truth the generator writes the incident from; never named in the incident text | `hardware_failure`, `link_circuit_carrier`, `routing_bgp`, `change_induced_errors`, `capacity_congestion`, `dns`, `power_environmental`, `security`, `software_firmware_bug`, `third_party_upstream`, `not_toil`, `new_category` | The category, whenever the evidence supports one |
| blast_radius | How widely the failure spreads, and whether redundancy absorbed it | `absorbed`, `one_site`, `multi_site` | Nothing in the label; it varies the incident text only |

### How the expected label is derived

<!-- Confidence bands follow 01_Product_Engineering/challenge/classifier.py.
     A misleading row must never expect the tempting category. -->

| evidence | surface_vs_cause | suggested_category | category_status | needs_human | confidence |
| --- | --- | --- | --- | --- | --- |
| complete | direct | the hidden category | `approved` | `false` | >= 0.8 |
| complete | misleading | the hidden category, not the tempting one | `approved` | `false` | >= 0.8 |
| partial | direct | the hidden category | `approved` | `false` | >= 0.8 |
| partial | misleading | the hidden category, not the tempting one | `approved` | `false` | >= 0.8 |
| conflicting | any | the hidden category, as the leading hypothesis (`null` when the hidden cause is `new_category`) | `approved` (`unclassified` when `new_category`) | `true` | 0.31-0.49 (<= 0.3 when `new_category`) |
| absent | any | `null` | `unclassified` | `true` | <= 0.3 |

**Partial rule:** the resolution is documented, so the cause is established. If the
category can be identified at >= 0.8 ("cause established + clear category match"),
it needs no review. Misleading rows follow the same rule.

**When `outcome_type` overrides the table:**
- `not_toil`: `not_toil`, `approved`, `needs_human: false`, >= 0.8 — for `complete` and `partial`. Generated only as planned, announced work whose impact matched the announcement; the record must say so. Planned work that caused more impact than announced is `change_induced_errors`. Under `conflicting` it is the leading hypothesis, sent for review; under `absent`, unclassified.
- `new_category`: an invented snake_case name, `new`, `needs_human: true`, 0.5-0.69 — for `complete` and `partial`. Under `conflicting` and `absent`, unclassified.

### How the category is chosen

Not uniformly. Each label group has a row quota, 400 in total, and combinations are sampled at random within a group until the quota is reachable after losses (`QUOTA`, `plan_rounds()` in `generate.py`):

| Group | Rows | | Group | Rows |
| --- | ---: | --- | --- | ---: |
| absent | 60 | | software_firmware_bug | 37 |
| conflicting | 20 | | link_circuit_carrier | 32 |
| not_toil | 40 | | third_party_upstream | 21 |
| new_category | 12 | | capacity_congestion | 19 |
| change_induced_errors | 79 | | routing_bgp | 13 |
| hardware_failure | 43 | | power_environmental | 11 |
| | | | security | 8 |
| | | | dns | 5 |

This replaces the charter's original 240 / 40 / 10. The shares come from published network-incident studies (Meza et al., IMC 2018; Turner et al., SIGCOMM 2010; Wu et al., SIGCOMM 2012 as cited by Meza) where they exist, and are assumed elsewhere; `decisions.md` (Week 2) tags each one. A uniform grid would have made a quarter of the rows declines and given every category the same volume. Within a group, rows are spread evenly over `surface_vs_cause` and `blast_radius`, which is also an assumption.

### Dead combinations, removed on purpose

| Combination | Why it cannot exist | Combinations removed |
| --- | --- | --- |
| `misleading_ddos` × `security` | A surface that looks like an attack is not misleading when the hidden cause is an attack | 12 |
| `misleading_dns` × `dns` | A surface that looks like a DNS outage is not misleading when the hidden cause is DNS | 12 |
| Not dead, not sampled | 219 of the 408 live combinations were never called. They can exist; the quota did not need them | — |

### Considered and rejected

| Axis | Why it is not in the grid |
| --- | --- |
| history / PRB match | Not in scope for this prototype - this would make sense to include when creating data for backfill feature|
| vendor | Maximum issues are vendor agnostic - and vendor related issues do not come under incident resolution for my team - they are handled by the vendor |
| device role | not significant enough to consider |
| paired site | not significant enough to consider |
| who writes it | Makes no difference to toil identification |

## What it can validate

<!-- Which claims this data supports. Be narrow. -->
**Kind of data: prototyping, with designed labels.** Every row has an expected output, so it has the shape of backtesting data, but those outputs were set by code from the axes each row was generated for, and no person has checked them.

Each claim below holds only for incidents written like these.

| This data can measure whether ToilMap… | Rows | Limit: a pass here does not prove it at work, because… |
| --- | ---: | --- |
| sends the incident to a person when the record never established a cause | 60 | every one of these records says plainly that no cause was found; a real ticket may hide that in a vague closing note |
| avoids the category a misleading surface imitates (`security` for DDoS-like symptoms, `dns` for DNS-like ones) | 259 | only two kinds of misleading surface were generated; real incidents mislead in ways nobody wrote down here |
| returns the designed category when the cause is established | 308 | the labels are unchecked, and some categories are too small to measure on their own (`dns` 5, `security` 8, `power_environmental` 11) |
| offers a leading hypothesis, sent for review, when the record leans one way without confirming it | 20 | 20 rows, and the label depends on the model having written a leaning record; in the pilot, half did not |
| recognises that no existing category fits, proposes a new name, and sends it to a person | 12 | 12 rows, and several of the invented causes (`memory_leak`, `vendor_firmware_regression`, `session_resource_exhaustion`) arguably fit an existing category, so the "new" label itself is the least certain in the data |
| always returns one of the three allowed outcome types | 400 | every incident here passed the completeness checks; nothing tests a ticket with missing fields, empty notes or very long text |

## What it cannot validate

<!-- The important half. Synthetic data cannot tell you about real distribution,
     real frequency, or failure modes you did not think to generate. Say so. -->
Every expected output is set by code from the axes the row was generated for, and no person has checked them. A score here measures agreement with the intended label; if an incident drifted from its axes, the label is wrong and the score cannot tell.
All 400 incidents were written by one 9B model, seeded with five long, well-written public RCAs. Real tickets are often terse, inconsistent or incomplete, and none of that style is here.
Only 120 of 400 rows record hands-on minutes, and those values were invented by the model with no reference distribution, so the hours rollup cannot be checked.
It cannot truly validate if human review load will remain below a target threshold with real data - at present all I will be able to know with certainity is the count of incidents sent to human review in this dataset
In a 50-row read sampled across every group, 7 labels (14%) did not fit the incident as written; new category was worst (2 of 2), then not_toil (2 of 5). Those rows were removed, along with 8 more not_toil rows found by checking the whole group, but the rest of the 400 were not read, so a similar share of unfitting labels may remain.
`not_toil` is generated only as planned, announced work. The taxonomy also allows a genuine one-off accident, such as a contractor cutting a duct once, but none were generated, so this data cannot show how ToilMap handles them.

## What it must never be compared against

<!-- If you have real ground truth somewhere, say where, and say explicitly that
     these rows are not it. -->
- **This tool is not the substitute for actual incident reports noted in my company's production environment.** Tests on a 400 row dataset cannot accurately validate the tool's performance on real-world scenarios. This test can only tell me how this tool performs against this given dataset
- **The goldens.** The data was based off the goldens, so the data cannot be compared against the goldens.
- **The team's perceived top-10 toil list.** Looking at the most proable causes of toil incidents, these 10 categories were picked. The data cannot be compared against this list, as the data was generated based on these categories.

## Leakage check — outward (what left)

- [x] No real record was used as a seed.
- [x] No real entity names, IDs, or identifiers appear.
- [x] No distinctive internal formats that would identify the firm.
- [x] Rare categories were generated, not copied.

Automated check (`sdg.leak_check` over the dataset): 0 hits. That finds names and identifiers only; the boxes above are ticked by a person after reading.

**Rows I read:** 50, sampled at random across all 14 label groups in proportion to their quota, at least 2 each (seed 7).

**What I removed after reading, and why** (15 rows, kept in `synthetic_v1.removed.jsonl`):
- From the 50-row read, labels that do not fit the incident as written:
  - SYN-0088, not_toil: a manually added static route caused a loop, which is a change-induced error.
  - SYN-0104, not_toil: a PSU failed from a capacitor leak, which is a hardware failure.
  - SYN-0132, new category: a config file removed a health-check target, which is `change_induced_errors`.
  - SYN-0129, new category: a known microcode bug, which is `software_firmware_bug`.
  - SYN-0064, conflicting, labelled `dns`: the competing explanations are an ACL rule and hardware, not DNS.
  - SYN-0006, absent: the record establishes a brute-force attempt, which is `security`.
  - SYN-0296, link: carrier line cards shut down from cabinet overheating, which is power or hardware.
- From checking every not_toil row against the new definition, rows with no sign in the text that the event was planned: SYN-0086 (PSU failure), SYN-0094 (deployment script blocked traffic), SYN-0099 (provider fibre cut), SYN-0100 (provider repair, not announced), SYN-0105 (browser vendor update bug), SYN-0106 (manual router reboot), SYN-0116 (provider emergency repair), and SYN-0416 (surplus).


## Leakage check — inward (what the eval shares with the training data)

**Are the goldens disjoint from anything the system was, or will be, tuned on?**
No — overlap. The goldens and the system were adjusted to fit each other in three places:

- **A golden was changed to stay in scope.** Its original expected outcome was out of scope for ToilMap, so I adjusted it to an in-scope outcome rather than keep an impossible edge case the tool could never produce. The golden is GS-05. The original outcome was "Not Toil" but the tool could never produce that outcome for this scenario.

- **GS-03, GS-04 and GS-05 had their confidence bands changed** in Week 2 to match the bands in `classifier.py` (commit `a9b00a7`): GS-03 to 0.31–0.49, GS-04 to 0.5–0.69, GS-05 to at most 0.3. This needed to be modified because my confidence scoring range became more granula to accomodate for more edge cases, and the original bands were too restrictive.

- **The classifier prompt was changed after GS-05 failed** in Week 1: it crashed on invalid JSON, and the output format in the prompt was regenerated from the schema (`decisions.md`, Week 1). This was done to ensure the tool could handle the expected output format.

So a score on the goldens measures whether ToilMap is consistent with its own design, not independent correctness. This synthetic data was generated from the goldens, so it shares that dependence.

**Overlap between `golden.jsonl` and this file, by the dedupe measure:** 0 rows at threshold 0.7. The closest pair is 0.19 (GS-01 against a generated row).
