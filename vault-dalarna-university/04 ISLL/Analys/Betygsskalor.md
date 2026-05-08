---
tags: [analys, betyg]
up: "[[ISLL MOC]]"
status: första pass
---

# Betygsskalor

## Problematiska kursplaner

<a class="download-xlsx" href="04-ISLL/Analys/Betygsskalor.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (0 rader)</span></a>

> [!example]- 0 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |

## Syfte

Kartlägga **inkonsekventa betygsskalor** vid Högskolan Dalarna — typfallet är att kursnivån sätts i U/3/4/5 medan delmoment redovisas i U/G/VG (eller tvärtom). Vissa fall är medvetna; de bör listas som undantag i koden.

## Metod

`qa/check_kursplaner.py` letar i sektionen `## Betyg` efter mönstret `\bU\s*[,/]\s*3\b` följt av `\bU\s*[,/]\s*[GV]\b` (eller tvärtom). Kursplaner som uttryckligen är undantagna anges i `MIXED_SCALE_EXEMPT` i [`qa/check_kursplaner.py`](../../qa/check_kursplaner.py).

**Begränsningar:** Regex är konservativ. Den missar betygskolumner som beskrivs i prosa eller med ovanlig formattering. Manuell granskning rekommenderas för flaggade fall.

## Datakälla

- Alla kursplaner under `0X {INST}/Kursplaner/` (IIT + IHV + IKS + ISLL)
- Endast sektionen `## Betyg`

## Rekommendationer

1. **Bekräfta varje A–F-fynd** mot beslutsmotivering — om motiverat, lägg till i en förteckning av undantag i denna fil.
2. **Korrigera inkonsekventa delskalor** vid nästa revidering, eller lägg till i `MIXED_SCALE_EXEMPT` om det finns ett pedagogiskt skäl att blanda.
3. **Lyft frågan i berörda kvalitetsutskott** — bör en standardiserad praxis fastställas på institutionsnivå?
