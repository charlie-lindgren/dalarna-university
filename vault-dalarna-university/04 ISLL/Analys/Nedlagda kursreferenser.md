---
tags: [analys, nedlagda-referenser]
up: "[[ISLL Analys]]"
status: första pass
---

# Nedlagda kursreferenser

## Problematiska utbildningsplaner

<a class="download-xlsx" href="04-ISLL/Analys/Nedlagda-kursreferenser.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (4 rader)</span></a>

> [!example]- 4 fynd — klicka för att expandera
>
> | Kursplan | Sida | Ämne | Fastställd | Reviderad | Problem | Detalj | Förslag |
> | --- | --- | --- | --- | --- | --- | --- | --- |
> | [LG79A](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=LG79A) | <a class="no-graph" href="04-ISLL/Utbildningsplaner/LG79A">sida</a> | Utbildningsplan | 2023-12-20 | 2024-02-14 | Programmet listar nedlagd kurs | `Didaktik och ledarskap för ämneslärare` | `PG1020` (nedlagd 2018-07-02) — plain-text-referens |
> | [LGGYA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=LGGYA) | <a class="no-graph" href="04-ISLL/Utbildningsplaner/LGGYA">sida</a> | Utbildningsplan | 2023-12-20 | 2024-02-14 | Programmet listar nedlagd kurs | `Didaktik och ledarskap för ämneslärare` | `PG1020` (nedlagd 2018-07-02) — plain-text-referens |
> | [LLF3A](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=LLF3A) | <a class="no-graph" href="04-ISLL/Utbildningsplaner/LLF3A">sida</a> | Utbildningsplan | 2023-12-20 | — | Programmet listar nedlagd kurs | `Text, kommunikation och lärande i en mångkulturell skola` | `GSV22L` (nedlagd 2024-10-11) — plain-text-referens |
> | [LLL3A](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=LLL3A) | <a class="no-graph" href="04-ISLL/Utbildningsplaner/LLL3A">sida</a> | Utbildningsplan | 2023-12-20 | — | Programmet listar nedlagd kurs | `Text, kommunikation och lärande i en mångkulturell skola` | `GSV22L` (nedlagd 2024-10-11) — plain-text-referens |

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
