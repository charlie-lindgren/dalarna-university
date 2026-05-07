---
tags: [analys, betyg]
up: "[[IHV MOC]]"
status: första pass
---

# Betygsskalor

## Problematiska kursplaner

<a class="download-xlsx" href="02-IHV/Analys/Betygsskalor.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (0 rader)</span></a>

> [!example]- 0 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |

## Syfte

Kartlägga vilka betygsskalor som används vid Högskolan Dalarna och flagga **avvikare** som inte följer institutionens standardpraxis. Två typiska avvikelser:

- **A–F-skala** istället för svensk standard (U/G/VG eller U/3/4/5).
- **Inkonsekvent delskalor** — kursnivån sätts i U/3/4/5 men delmoment redovisas i U/G/VG (eller tvärtom). Vissa fall är medvetna; de bör listas som undantag.

## Metod

`qa/check_kursplaner.py` letar i sektionen `## Betyg` efter:

- **A–F-mönster:** `\bA\s*[–\-]\s*F\b` eller komma-separerad form `A, B, C, D, E`.
- **Inkonsekvent delskalor:** `\bU,3\b` följt av `\bU,[GV]\b` (eller motsvarande).

Kursplaner som uttryckligen är undantagna från flaggning anges i `MIXED_SCALE_EXEMPT` i [`qa/check_kursplaner.py`](../../qa/check_kursplaner.py).

**Begränsningar:** Regex är konservativ. Den missar betygskolumner som beskrivs i prosa eller med ovanlig formattering. Manuell granskning rekommenderas för flaggade fall.

## Datakälla

- Alla kursplaner under `0X {INST}/Kursplaner/` (IIT + IHV + IKS + ISLL)
- Endast sektionen `## Betyg`

## Resultat

*Fylls i efter första genomgång.*

## Observationer

*Fylls i efter första genomgång. Förväntad bild: A–F förekommer främst på fristående kurser och utbytesprogram (legitima skäl); inkonsekventa delskalor uppstår vid revideringar där delmomentens skala inte uppdaterades samtidigt som kursens.*

## Rekommendationer

1. **Bekräfta varje A–F-fynd** mot beslutsmotivering — om motiverat, lägg till i en förteckning av undantag i denna fil.
2. **Korrigera inkonsekventa delskalor** vid nästa revidering, eller lägg till i `MIXED_SCALE_EXEMPT` om det finns ett pedagogiskt skäl att blanda.
3. **Lyft frågan i berörda kvalitetsutskott** — bör en standardiserad praxis fastställas på institutionsnivå?
