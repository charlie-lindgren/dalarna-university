---
check: Examinationsformer
---

## Purpose
<!-- sv cb5180b2 -->

The `Examinationsformer` section (forms of assessment) should present the parts of the examination as a **bulleted list**. Running text makes the parts unclear and harder to read, both for students and for Ladok administration.

## Method
<!-- sv 34e8207f -->

Each syllabus is checked: if the `Examinationsformer` section has content but no bulleted list (lines starting with *-* or *\**), it is flagged.

**Limitations:**

- Numbered lists (*1. tentamen*) do not count as bulleted lists, which can give false positives.
- A review by hand is needed to tell formatting faults from real problems.

## Data source
<!-- sv 9a8b965c -->

- All course syllabi at Dalarna University, from du.se (IIT, IHV, IKS, ISLL).
- Only the `Examinationsformer` section.

## Recommendations
<!-- sv 16fa197a -->

1. **Add the Ladok code for each component** at the next revision of the flagged syllabi.
2. **When there is only one component**, still use a bullet and give the code, so that the format is predictable.
3. **Discuss with the Ladok administrator** whether some syllabi leave out the examination code on purpose, for reasons of fairness or history.
