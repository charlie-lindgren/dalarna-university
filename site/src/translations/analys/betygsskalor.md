---
check: Betygsskalor
---

## Purpose
<!-- sv e299f127 -->

To identify **inconsistent grading scales** at Dalarna University. The typical case is a course graded U/3/4/5 as a whole while its components are graded U/G/VG (or the other way round). Some cases are deliberate; they should be listed as exceptions.

## Method
<!-- sv 37c497ed -->

The `Betyg` section (grades) is searched for mixed scales: a course whose final grade is on U/3/4/5 while its components are graded U/G/VG, or the other way round. Syllabi that are explicitly exempted are kept in a curated list.

**Limitations:** The detection is conservative. It misses grading described in prose or formatted in an unusual way. Flagged cases should be reviewed by hand.

## Data source
<!-- sv 8f704687 -->

- All course syllabi at Dalarna University, from du.se (IIT, IHV, IKS, ISLL).
- Only the `Betyg` section.

## Recommendations
<!-- sv 966504dd -->

1. **Confirm each finding** against the reasons given for the decision. If it is justified, add it to the list of approved exceptions.
2. **Correct inconsistent component scales** at the next revision, or add them to the list of exceptions if there is an educational reason to mix them.
3. **Raise the question in the quality committees concerned.** Should a standard practice be set at school level?
