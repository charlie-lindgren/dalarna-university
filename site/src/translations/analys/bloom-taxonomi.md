---
check: Bloom-taxonomi
---

## Purpose
<!-- sv 5575f983 -->

The **level of the verbs in the learning outcomes should match the level of the course**. A second-cycle course whose outcomes stay at the Remember and Understand levels suggests that the course sits lower cognitively than its level says. A first-cycle course dominated by Evaluate and Create verbs may point to a wrong classification, or to a course that really belongs to the second cycle. This is both an educational and a formal problem (the Bologna framework, the Higher Education Ordinance).

## Method
<!-- sv 1c486d40 -->

For each bullet in the `Lärandemål` section (learning outcomes, Swedish version), the **first verb that can be classified** is matched against a Swedish verb lexicon ordered by the six levels of the revised Bloom taxonomy (1 Remember → 2 Understand → 3 Apply → 4 Analyse → 5 Evaluate → 6 Create). Leading adverbs (*självständigt*, independently; *muntligt*, orally) are skipped. The course level is read from the syllabus's metadata (*Grundnivå*, first cycle, or *Avancerad nivå*, second cycle), not from the prefix of the course code, since a prefix such as G2 can in fact denote the first cycle.

Three rules produce findings:

- **Low verb level for a second-cycle course.** The course is second cycle, but no outcome is at level 4 to 6 (Analyse, Evaluate, Create).
- **High verb level for a first-cycle course.** The course is first cycle, but at least 60% of the classified outcomes are at level 5 or 6 (Evaluate, Create).
- **Unknown verb.** At least 3 outcomes begin with a verb the lexicon does not have. This is not a quality fault in itself, but a sign that the lexicon should grow.

The detail text for each finding shows the spread as a histogram of six cells, for example *fördelning [2,3,1,0,0,0]* (distribution; cell 1 is Remember, cell 6 is Create).

**Limitations:**

- The lexicon is curated by hand and incomplete. It grows step by step from the unknown verbs found.
- Context is not taken into account: *"redogöra för komplexa samband"* (give an account of complex relationships) can be a demanding outcome despite its Remember verb.
- When a verb sits at two levels (for example *jämföra*, compare, between Understand and Analyse), the higher level is always chosen.
- Only Swedish is analysed; the English Learning Outcomes are not examined here.

The list is meant as a basis for discussion. The reviewer judges each finding in its context.

## Data source
<!-- sv 06b63551 -->

- All course syllabi at Dalarna University, from du.se (IIT, IHV, IKS, ISLL).
- Only the Swedish version, the `Lärandemål` section.
- The course level is read from the syllabus's metadata (*Grundnivå* or *Avancerad nivå*).

## Recommendations
<!-- sv 10e4a08b -->

1. **Review each flagged syllabus by hand**, with context from the course's aim, examination and literature.
2. **Add learning outcomes with higher Bloom verbs** at the next revision, if the context confirms that the course really is at second-cycle level.
3. **Consider changing the level** if there is a consistent pattern of low verbs. Perhaps the course should be first cycle.
