---
check: Stavfel och språkbruk
---

## Purpose
<!-- sv fd65e7dd -->

To identify **obvious writing errors** (repeated words, known misspellings, words not in the dictionary) in course syllabi across Dalarna University's four schools. Misspellings do not only hinder reading; they also undermine the impression of quality assurance.

## Method
<!-- sv 4fe716dd -->

Four checks are run on each syllabus:

1. **Repeated words**, for example *modeller modeller*, except for legitimate repetitions (*för för*, *och och*).
2. **Known misspellings.** A curated list of recurring typos in Swedish and in English text. Each finding shows both the wrong form and the suggested correction.
3. **Swedish spell check.** Flags words that are not in the Swedish dictionary and occur in fewer than four syllabi (a rare word is more likely a typo, a common one more likely a term of the field).
4. **English spell check.** The same logic against the English version, with a threshold of fewer than 5 syllabi.

Both spell checks are filtered against extensive ignore lists (terms of the field, acronyms, British spellings) that are maintained and extended step by step.

**Limitations:** The spell check misses errors that depend on context (*var/vart*, *de/dem*). Proper names and technical terms can give false hits until they are added to the ignore list.

## Data source
<!-- sv 0d3c22dd -->

- All course syllabi at Dalarna University, from du.se (IIT, IHV, IKS, ISLL).
- Swedish text: the syllabus's body text, excluding the `English Version` part.
- English text: only the `English Version` part.

## Recommendations
<!-- sv 9d899140 -->

1. **Correct confirmed misspellings** at the next revision of each syllabus.
2. **Check words that look run together** (for example *shouldbe*, *buildingprocess*) against the source on du.se. They sometimes arise when text is copied without the right spaces.
3. **Run the analysis regularly**, so that new syllabi are caught early.
