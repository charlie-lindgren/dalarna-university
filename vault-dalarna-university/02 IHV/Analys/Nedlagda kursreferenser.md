---
tags: [analys, nedlagda-referenser]
up: "[[IHV Analys]]"
status: första pass
---

# Nedlagda kursreferenser

## Problematiska utbildningsplaner

<a class="download-xlsx" href="02-IHV/Analys/Nedlagda-kursreferenser.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (2 rader)</span></a>

> [!example]- 2 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [VBSKA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VBSKA) | Utbildningsplan | Programmet listar nedlagd kurs | `Gynekologisk och postpartumvård, verksamhetsförlagd utbildning` → `VÅ3086` (nedlagd 2017-04-07) — plain-text-referens |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programmet listar nedlagd kurs | `Introduktion omvårdnad och etik - Huvudområde Omvårdnad` → `VÅ1061` (nedlagd 2025-06-03) — plain-text-referens |

## Syfte

Sektionen *Programmets kurser* i en utbildningsplan listar de kurser som ingår i programmet. När en kurs på du.se markeras som nedlagd försvinner den ur HDa:s aktiva katalog, men utbildningsplanens text uppdateras inte automatiskt — kvar blir referenser till kurser som inte längre erbjuds. Syftet med analysen är att kartlägga **vilka utbildningsplaner som fortfarande listar nedlagda kurser** så att texten kan revideras innan studenter förlitar sig på en inaktuell kursförteckning.

## Metod

`qa/check_utbildningsplaner.py` parsar varje utbildningsplans `## 3. Programmets kurser`-sektion och plockar ut kursbullets i tre former: `[[CODE|Namn]]`-wikilänk, `<a class="no-graph" href="CODE">…</a>` (korsinstitutionell länk) och oklassad text (kursnamn utan kursplankodsmatchning). Varje träff slås upp mot QA-cachen i `qa/nedlagda-kursplaner/` — antingen via kurskod (för länkar) eller via namnnormalisering (för plain-text-bullets). En träff betyder att den listade kursen har `status=discontinued` på du.se och därför inte längre kan läsas.

## Datakälla

- Samtliga utbildningsplaner i `0X {INST}/Utbildningsplaner/`.
- QA-cache av nedlagda kursplaner: `qa/nedlagda-kursplaner/` (skrapas via menyval 7 i `hda.sh`).

## Rekommendationer

1. **Byt referens till ersättningskursen** — när en nedlagd kurs har en aktuell efterträdare (samma huvudområde, samma omfattning) uppdateras utbildningsplanens kurslista till den nya koden/namnet.
2. **Stryk kursen ur programmet** — när det inte finns en ersättare och kursen inte längre är avgörande för examensmålen, ta bort referensen och justera programmets totala omfattning vid behov.
3. **Lyft till programansvarig** — utbildningsplanens kurslista är ett beslut för programansvarig; QA-rapporten visar var ändringar behövs men inte vilken väg som är rätt.
