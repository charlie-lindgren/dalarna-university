---
tags: [analys, betyg]
up: "[[IIT Analys]]"
status: första pass
---

# Betygsskalor

## Problematiska kursplaner

<a class="download-xlsx" href="01-IIT/Analys/Betygsskalor.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (11 rader)</span></a>

> [!example]- 11 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [BY3005](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BY3005) | BYA | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GBY2J2](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GBY2J2) | BYA | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GBY2XF](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GBY2XF) | BYA | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GSQ23K](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ23K) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GSQ25F](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ25F) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GSQ25K](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ25K) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GSQ2J4](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ2J4) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GSQ2L8](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ2L8) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GSQ2PH](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ2PH) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GSQ33M](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ33M) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |
> | [GSQ33N](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ33N) | SQQ | Inkonsekvent delskalor | Inkonsekvent delskalor: kursnivå U,3,4,5 men VG nämns i delmoment |

## Syfte

Kartlägga **inkonsekventa betygsskalor** vid Högskolan Dalarna — typfallet är att kursnivån sätts i U/3/4/5 medan delmoment redovisas i U/G/VG (eller tvärtom). Vissa fall är medvetna; de bör listas som undantag.

## Metod

I sektionen `Betyg` letas mönster av blandade skalor: en kurs med totalbetyg i U/3/4/5 vars delmoment redovisas i U/G/VG, eller tvärtom. Kursplaner som uttryckligen är undantagna upprätthålls i en kurerad lista.

**Begränsningar:** Detektionen är konservativ. Den missar betygskolumner som beskrivs i prosa eller med ovanlig formatering. Manuell granskning rekommenderas för flaggade fall.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna (IIT, IHV, IKS, ISLL).
- Endast sektionen `Betyg`.

## Rekommendationer

1. **Bekräfta varje fynd** mot beslutsmotivering — om motiverat, lägg till i förteckningen över godkända undantag.
2. **Korrigera inkonsekventa delskalor** vid nästa revidering, eller lägg till i undantagsförteckningen om det finns ett pedagogiskt skäl att blanda.
3. **Lyft frågan i berörda kvalitetsutskott** — bör en standardiserad praxis fastställas på institutionsnivå?
