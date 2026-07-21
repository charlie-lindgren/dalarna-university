---
tags: [analys, programkurser]
up: "[[IHV Analys]]"
status: första pass
---

# Programkurser olänkade

## Bakgrund

Utbildningsplanens `## 3. Programmets kurser`-sektion ska helst lista varje kurs som en wikilänk till motsvarande kursplansfil (`[[KOD|Namn]], hp`). Analysen flaggar två typer av problem: **olänkade bullets** (där länken saknas helt) och **länkade bullets där programtexten avviker från kursplanens kanoniska namn** (vår skrapa hittar fortfarande rätt kurs via normalisering, men texten bör samordnas).

Tabellen delar upp fyndet i två kolumner: **Detalj** är kursnamnet så som utbildningsplanen skriver det, **Förslag** är den kurs vi bedömer att raden syftar på (med kurskod). Rader med `—` i Förslag saknar ännu en kandidat — antingen för att kursen verkligen inte finns i HDa:s katalog, eller för att programtexten är för tvetydig för att peka ut en enskild kurs. Förslagen kommer från en handkurerad mappning i [qa/checks_nedlagda.py](../../qa/checks_nedlagda.py) (`_KANDIDAT_MATCHNINGAR_RAW`) och kan fyllas på efter hand.

## Problematiska utbildningsplaner

<a class="download-xlsx" href="02-IHV/Analys/Programkurser-olänkade.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (5 rader)</span></a>

> [!example]- 5 fynd — klicka för att expandera
>
> | Kursplan | Sida | Ämne | Fastställd | Reviderad | Problem | Detalj | Förslag |
> | --- | --- | --- | --- | --- | --- | --- | --- |
> | [VBSKA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VBSKA) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VBSKA">sida</a> | Utbildningsplan | 2019-09-10 | — | Programtext avviker från kursplanens namn | `Gravididet, förlossning och postpartumvård 1` (7,5 hp) | `Graviditet, förlossning och postpartumvård I` (kurskod `ASR29T`) |
> | [VBSKA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VBSKA) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VBSKA">sida</a> | Utbildningsplan | 2019-09-10 | — | Programtext avviker från kursplanens namn | `Gravididet, förlossning och postpartumvård 2` (6 hp) | `Graviditet, förlossning och postpartumvård II` (kurskod `ASR2AD`) |
> | [VGSEA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VGSEA) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VGSEA">sida</a> | Utbildningsplan | 2021-03-04 | — | Programtext avviker från kursplanens namn | `Strategier för implementering av förbättringsarbete i hälso-sjukvård` (7,5 hp) | `Strategier för implementering av förbättringsarbete i hälso- och sjukvård` (kurskod `ASR2CG`) |
> | [VIDRG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VIDRG) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VIDRG">sida</a> | Utbildningsplan | 2025-01-15 | — | Programtext avviker från kursplanens namn | `Media och kommunikation inom idrott` (7,5hp) | `Medier och kommunikation inom idrott` (kurskod `GIH3GF`) |
> | [VSADA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSADA) | <a class="no-graph" href="02-IHV/Utbildningsplaner/VSADA">sida</a> | Utbildningsplan | 2023-01-09 | — | Programtext avviker från kursplanens namn | `Personcentrerad vård av personer med demens` (7,5 hp) | `Personcentrerad vård för personer med demens` (kurskod `VÅ3127`) |

## Syfte

Att skilja **kvalitetsproblem på programsidan** (okända kursnamn, trunkerade rader) från **brister i vår skrapa** (aktiv kurs hittades inte och länkades inte) samt från **legitima alternativbullets** (val mellan flera kurser) — så att rätt åtgärd kan vidtas.

## Metod

`qa/check_utbildningsplaner.py` parsar varje utbildningsplans `## 3. Programmets kurser`-sektion och plockar ut alla kursbullets via `scan_programme_bullets` i [qa/checks_nedlagda.py](../../qa/checks_nedlagda.py). För varje bullet som saknar wikilänk eller no-graph-anchor klassas namnet enligt:

| Kategori | Indikator |
|----------|-----------|
| **Okänd kursreferens i program** | Namnet matchar varken aktiv kursplan eller nedlagda-arkivet |
| **Aktiv kurs olänkad (scraper-miss)** | Namnet matchar en aktiv kursplan i vaulten (vår skrapa borde ha länkat) |
| **Alternativ-bullet (val mellan kurser)** | Innehåller `eller`, `alternativt`, `valbar` eller ` / ` |
| **Trunkerad kursrad** | Oavslutad parentes eller hängande `eller`/`och`/`,` på radslutet |
| **Programtext skiljer från kursnamn** | Bulleten *är* länkad men alias-texten skiljer sig från kursplanens `kursnamn:` (t.ex. `System- och verksamhetsutveckling` vs `System och verksamhetsutveckling`) |

Träffar mot **nedlagda kursplaner** rapporteras separat i [[Nedlagda kursreferenser]] och dyker inte upp här.

## Datakälla

- Samtliga utbildningsplaner i `0X {INST}/Utbildningsplaner/`.
- Aktiva titlar och kurskoder från vaultens `Kursplaner/`-träd.
- QA-cache av nedlagda kursplaner: `qa/nedlagda-kursplaner/`.

## Rekommendationer

1. **Okänd kursreferens i program** är ett innehållsfel i utbildningsplanen — kursnamnet stämmer inte mot HDa:s katalog. Möjliga orsaker: stavfel, kursen aldrig publicerad på du.se, eller felaktig benämning. Lyft till programansvarig.
2. **Aktiv kurs olänkad** är ett scraper-fel hos oss; raden ska komma in som en wikilänk vid nästa skrapning. Granska `scripts/scrape_hda_utbildningsplaner.py` om kategorin växer.
3. **Alternativ-bullet** är legitim — programmet låter studenten välja mellan kurser. Ingen åtgärd om bullet är välformulerad.
4. **Trunkerad kursrad** är typiskt en parsefel — antingen i scrapern eller i den ursprungliga du.se-texten. Granska den rapporterade raden.
5. **Programtext skiljer från kursnamn** kräver att programansvarig uppdaterar kurslistan i utbildningsplanen så att texten matchar kursplanens officiella namn. Vanligaste orsaken är svensk ellipsis (`X- och Y` istället för `X och Y`).
6. **Förslagskolumnen är ett underlag, inte ett beslut.** Kontrollera kurskoden mot du.se innan programtexten rättas — särskilt när flera kurser delar snarlika namn (t.ex. `… åk 7-9` vs `… gymnasieskolan`). Rader utan förslag behöver utredas manuellt med programansvarig; när svaret är känt kan mappningen kompletteras så att förslaget dyker upp automatiskt vid nästa körning.
