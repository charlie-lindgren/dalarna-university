---
tags: [analys, nedlagda-referenser]
up: "[[IHV Analys]]"
status: första pass
---

# Nedlagda kursreferenser

## Problematiska utbildningsplaner

<a class="download-xlsx" href="02-IHV/Analys/Nedlagda-kursreferenser.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (6 rader)</span></a>

> [!example]- 6 fynd — klicka för att expandera
>
> | Kursplan | Sida | Ämne | Fastställd | Reviderad | Problem | Detalj | Förslag |
> | --- | --- | --- | --- | --- | --- | --- | --- |
> | [VBSKA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VBSKA) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VBSKA">sida</a> | Utbildningsplan | 2019-09-10 | — | Programmet listar nedlagd kurs | `Gynekologisk och postpartumvård, verksamhetsförlagd utbildning` | `VÅ3086` (nedlagd 2017-04-07) — plain-text-referens |
> | [VSJPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSJPG) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VSJPG">sida</a> | Utbildningsplan | 2023-11-07 | — | Programmet listar nedlagd kurs | `Metoder för evidensbaserad vård II` | `GVÅ2ZY` (nedlagd 2026-09-04) — wikilink-länk till nedlagd kod |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VSSKG">sida</a> | Utbildningsplan | 2018-12-04 | 2020-12-17 | Programmet listar nedlagd kurs | `Introduktion omvårdnad och etik - Huvudområde Omvårdnad` | `VÅ1061` (nedlagd 2025-06-03) — plain-text-referens |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VSSKG">sida</a> | Utbildningsplan | 2018-12-04 | 2020-12-17 | Programmet listar nedlagd kurs | `Människans grundläggande omvårdnadsbehov - Huvudområde Omvårdnad` | `GVÅ2RA` (nedlagd 2026-09-04) — wikilink-länk till nedlagd kod |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VSSKG">sida</a> | Utbildningsplan | 2018-12-04 | 2020-12-17 | Programmet listar nedlagd kurs | `Metoder för evidensbaserad vård II - Huvudområde Omvårdnad` | `GVÅ2ZY` (nedlagd 2026-09-04) — wikilink-länk till nedlagd kod |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VSSKG">sida</a> | Utbildningsplan | 2018-12-04 | 2020-12-17 | Programmet listar nedlagd kurs | `Personcentrerad vård med fördjupning inom omvårdnad - Huvudområde Omvårdnad` | `GVÅ2ZG` (nedlagd 2026-09-04) — wikilink-länk till nedlagd kod |

## Syfte

Sektionen *Programmets kurser* i en utbildningsplan listar de kurser som ingår i programmet. När en kurs på du.se markeras som nedlagd försvinner den ur HDa:s aktiva katalog, men utbildningsplanens text uppdateras inte automatiskt — kvar blir referenser till kurser som inte längre erbjuds. Syftet med analysen är att kartlägga **vilka utbildningsplaner som fortfarande listar nedlagda kurser** så att texten kan revideras innan studenter förlitar sig på en inaktuell kursförteckning.

## Metod

Varje utbildningsplans kurslista (sektionen *Programmets kurser*) gås igenom kurs för kurs. Varje kurs — oavsett om den anges som länk eller som ren text — slås upp mot förteckningen över kurser som du.se har markerat som nedlagda. En träff betyder att kursen inte längre kan läsas men fortfarande listas i programmet.

## Datakälla

- Samtliga utbildningsplaner vid Högskolan Dalarna.
- Förteckningen över nedlagda kurser på du.se.

## Rekommendationer

1. **Byt referens till ersättningskursen** — när en nedlagd kurs har en aktuell efterträdare (samma huvudområde, samma omfattning) uppdateras utbildningsplanens kurslista till den nya koden/namnet.
2. **Stryk kursen ur programmet** — när det inte finns en ersättare och kursen inte längre är avgörande för examensmålen, ta bort referensen och justera programmets totala omfattning vid behov.
3. **Lyft till programansvarig** — utbildningsplanens kurslista är ett beslut för programansvarig; QA-rapporten visar var ändringar behövs men inte vilken väg som är rätt.
