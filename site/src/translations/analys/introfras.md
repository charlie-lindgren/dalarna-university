---
check: Introfras
---

## Purpose
<!-- sv 29b2e2e3 -->

The `Lärandemål` heading (learning outcomes) is expected to be followed directly by a phrase that begins *Efter ...* (usually *"Efter godkänd kurs ska studenten kunna:"*, on completion of the course, the student shall be able to). An introductory description, a course introduction or part-course headings in between can obscure the outcomes and make the structure uneven across the schools. The aim is to find **which syllabi have stray text between the heading and the introductory phrase**.

## Method
<!-- sv 8a64c784 -->

The `Lärandemål` section is extracted and its **first line that is not empty** is examined. If that line does not begin with *Efter* (in any letter case), the syllabus is flagged.

Accepted variants (all begin with *Efter*):

- *Efter godkänd kurs ska studenten kunna:*
- *Efter avslutad kurs skall den studerande kunna:*
- *Efter genomgången kurs ska studenten kunna:*
- *Efter avslutad delkurs ska den studerande kunna:*

The **exact wording** of the phrase is not examined here; that is done in [[Frasningskonsistens|Consistent wording]]. This analysis only checks that the heading is followed by *a* phrase that begins with *Efter*.

## Data source
<!-- sv 5091a95b -->

- All course syllabi at Dalarna University, from du.se.
- Only the Swedish section `Lärandemål`.

## Recommendations
<!-- sv 56785de0 -->

1. **Move introductory text** to `Kursinnehåll` (course content) or a similar section. `Lärandemål` should begin directly with the *Efter ...* phrase.
2. **Remove part-course headings** above the first phrase in a course made up of parts. Each part can instead have its own *Efter ... kunna* phrase under a shared heading.
3. **Raise the question in the quality committees concerned.** Should the frame around the learning outcomes be an explicit point in the schools' guidelines?
