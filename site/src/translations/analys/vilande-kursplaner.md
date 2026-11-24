---
check: Vilande kursplaner
---

## Purpose
<!-- sv a8db6200 -->

To identify courses that are **dormant**: their course page on du.se shows no active course offering. This is often legitimate, but it can also suggest that phasing out or archiving has not been completed.

## Method
<!-- sv c5d2d302 -->

1. The current course offering for each subject is fetched from du.se.
2. The list is compared with the courses published here.
3. For courses missing from the current offering, the syllabus page is checked directly.
4. Courses with no active offering (no *"Start vecka"*, start week) are marked as **dormant**.

**Limitations:**

- A dormant course is not automatically a fault; the analysis mainly shows what needs following up.
- If du.se gives wrong answers for a while, the classification can be uncertain until the next run.

## Data source
<!-- sv 5a877b28 -->

- The course offering lists and the syllabus pages on du.se, Dalarna University.
- The data are updated with each run.

## Recommendations
<!-- sv 576843c3 -->

1. Confirm with the subject's representatives whether each dormant course should be revived, kept or discontinued.
2. For courses that are to be discontinued, plan a move to a clear archived status.
3. Run the analysis regularly, to catch drift between the offering and the published syllabi.
