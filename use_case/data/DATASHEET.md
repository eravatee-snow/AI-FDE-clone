# Datasheet

<!-- Written in TC2, alongside your synthetic data. This file is committed; the
     data itself is not. -->

## What this data is

**Generated on:** <!-- date -->
**Generated from:** <!-- the schema + a written description, NOT real records -->
**Rows:** <!-- n -->

## Generation run

<!-- Filled in after Step 2. Enough for someone else to reproduce the run. -->

| Setting | Value |
| --- | --- |
| Model | <!-- e.g. ollama/llama3.1:8b, and the hardware it ran on --> |
| Temperature | <!-- --> |
| Top-p | <!-- --> |
| Dedupe threshold | <!-- --> |
| Rows per combination | <!-- --> |
| Seeds shown to the generator | <!-- which goldens, in what order --> |

| Count | Value |
| --- | --- |
| Generated | <!-- --> |
| After dedupe | <!-- --> |
| Schema-valid | <!-- --> |
| Dead combinations | <!-- n, and which --> |

## Variation axes

<!-- Must match 02_Open_Weights/challenge/axes.py: same axes, same values. -->

| Axis | What real variation it covers | Values | What it drives in the expected output |
| --- | --- | --- | --- |
| evidence | <!-- --> | `complete`, `partial`, `conflicting`, `absent` | <!-- --> |
| surface_vs_cause | <!-- --> | `direct`, `misleading_ddos` (looks like `security`), `misleading_dns` (looks like `dns`) | <!-- --> |
| outcome_type | <!-- --> | `hardware_failure`, `link_circuit_carrier`, `routing_bgp`, `change_induced_errors`, `capacity_congestion`, `dns`, `power_environmental`, `security`, `software_firmware_bug`, `third_party_upstream`, `not_toil`, `new_category` | <!-- --> |
| blast_radius | <!-- --> | `absorbed`, `one_site`, `multi_site` | <!-- --> |

### How the expected label is derived

<!-- Confidence bands follow 01_Product_Engineering/challenge/classifier.py.
     A misleading row must never expect the tempting category. -->

| evidence | surface_vs_cause | suggested_category | category_status | needs_human | confidence |
| --- | --- | --- | --- | --- | --- |
| complete | direct | the hidden category | `approved` | `false` | >= 0.8 |
| complete | misleading | the hidden category, not the tempting one | `approved` | `false` | <!-- --> |
| partial | direct | the hidden category | `approved` | `false` | >= 0.8 |
| partial | misleading | the hidden category, not the tempting one | `approved` | `false` | <!-- --> |
| conflicting | any | <!-- the leading hypothesis? --> | <!-- --> | <!-- --> | <!-- --> |
| absent | any | `null` | `unclassified` | `true` | < 0.3 |

**Partial rule:** the resolution is documented, so the cause is established. If the
category can be identified at >= 0.8 ("cause established + clear category match"),
it needs no review. <!-- confirm the misleading rows follow the same rule -->

**When `outcome_type` overrides the table:**
- `not_toil`: <!-- suggested_category not_toil, approved, needs_human false — for which evidence values? -->
- `new_category`: <!-- category_status new, needs_human true, confidence 0.5-0.69 — for which evidence values? -->

### How the category is chosen

<!-- e.g. every taxonomy category plus not_toil and new_category, crossed uniformly
     with the other axes. Say how this differs from the charter's mix
     (240 across 10 categories / 40 noise / 10 unconfirmed), or how you weighted it. -->

### Dead combinations, removed on purpose

| Combination | Why it cannot exist | Combinations removed |
| --- | --- | --- |
| `misleading_ddos` × `security` | <!-- --> | 12 |
| `misleading_dns` × `dns` | <!-- --> | 12 |
| <!-- --> | <!-- --> | <!-- --> |

### Considered and rejected

| Axis | Why it is not in the grid |
| --- | --- |
| history / PRB match | <!-- --> |
| vendor | <!-- --> |
| device role | <!-- --> |
| paired site | <!-- --> |
| who writes it | <!-- --> |

## What it can validate

<!-- Which claims this data supports. Be narrow. -->

## What it cannot validate

<!-- The important half. Synthetic data cannot tell you about real distribution,
     real frequency, or failure modes you did not think to generate. Say so. -->

## What it must never be compared against

<!-- If you have real ground truth somewhere, say where, and say explicitly that
     these rows are not it. -->

## Leakage check — outward (what left)

- [ ] No real record was used as a seed.
- [ ] No real entity names, IDs, or identifiers appear.
- [ ] No distinctive internal formats that would identify the firm.
- [ ] Rare categories were generated, not copied.

## Leakage check — inward (what the eval shares with the training data)

**Are the goldens disjoint from anything the system was, or will be, tuned on?**
<!-- yes, disjoint | no — overlap: <which goldens, which source> | unknown — who would know: <role> -->

**Overlap between `golden.jsonl` and this file, by the dedupe measure:** <!-- n rows at threshold t -->
