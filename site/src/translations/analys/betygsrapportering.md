---
check: Betygsrapportering
---

## Purpose
<!-- sv 532d3715 -->

The `## Betyg` section (grades) describes both the grading scale for the whole course and how modules and components are reported. The convention at Dalarna University is to list the grade reporting of modules and parts of a course as a **bulleted list**, so that examiners, study administration and students can quickly see which components count towards the final grade. When the section is written as running text instead, the structure is harder to read and syllabi become inconsistent across the schools. The aim of the analysis is to identify **which course syllabi have no bulleted list at all in the grades section**.

## Method
<!-- sv 636cd485 -->

The `## Betyg` section is extracted from the Swedish page. If the section has content but not a single bullet (`- ` or `* `), the syllabus is flagged. The grading scale itself and the consistency of the component scales are not examined here; that is done in [[Betygsskalor|Grading scales]]. This analysis is only concerned with whether **the structure is a bulleted list**.

Two main kinds are caught by the same flag:

1. Very short sections that only state the main scale, for example *"Som betygsskala används U–VG."* (the grading scale used is U–VG). These are syllabi with a single module, where a bulleted list would still have made the structure clearer.
2. Longer sections that list modules and grade reporting in running text. This is the typical case where a bulleted list would have made the section much easier to read.

## Data source
<!-- sv 61fea476 -->

- All course syllabi at Dalarna University, from du.se.
- Only the Swedish section `## Betyg`.

## Recommendations
<!-- sv 603b6bf7 -->

1. **Turn running text into a bulleted list.** Each module or component that is graded on its own becomes a bullet of its own, with credits and scale where relevant.
2. **Use a bulleted list for single-module courses too** where it makes sense, for example *"- Hel kurs (U–VG)"* (whole course), so that the subject presents its courses the same way.
3. **Raise the question in the quality committees concerned.** Should the schools share a template for how the grades section is structured (a bulleted list as standard, running text only by exception)?
