---
tags: [analys, betyg]
up: "[[Analys MOC]]"
status: första pass
---

# Betygsskalor

## Problematiska kursplaner

> [!example]- 4 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [GSQ25F](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ25F) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men delmoment i U,G,VG |
> | [GSQ2J4](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ2J4) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men delmoment i U,G,VG |
> | [GSQ2L8](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ2L8) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men delmoment i U,G,VG |
> | [GSQ2PH](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ2PH) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men delmoment i U,G,VG |

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

- Alla kursplaner under `01 Kursplaner/` (IIT + IHV + IKS + ISLL)
- Endast sektionen `## Betyg`

## Resultat

*Fylls i efter första genomgång.*

## Observationer

*Fylls i efter första genomgång. Förväntad bild: A–F förekommer främst på fristående kurser och utbytesprogram (legitima skäl); inkonsekventa delskalor uppstår vid revideringar där delmomentens skala inte uppdaterades samtidigt som kursens.*

## Rekommendationer

1. **Bekräfta varje A–F-fynd** mot beslutsmotivering — om motiverat, lägg till i en förteckning av undantag i denna fil.
2. **Korrigera inkonsekventa delskalor** vid nästa revidering, eller lägg till i `MIXED_SCALE_EXEMPT` om det finns ett pedagogiskt skäl att blanda.
3. **Lyft frågan i berörda kvalitetsutskott** — bör en standardiserad praxis fastställas på institutionsnivå?
