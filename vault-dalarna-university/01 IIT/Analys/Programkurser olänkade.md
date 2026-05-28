---
tags: [analys, programkurser]
up: "[[IIT Analys MOC]]"
status: första pass
---

# Programkurser olänkade

## Bakgrund

Utbildningsplanens `## 3. Programmets kurser`-sektion ska helst lista varje kurs som en wikilänk till motsvarande kursplansfil (`[[KOD|Namn]], hp`). Analysen flaggar två typer av problem: **olänkade bullets** (där länken saknas helt) och **länkade bullets där programtexten avviker från kursplanens kanoniska namn** (vår skrapa hittar fortfarande rätt kurs via normalisering, men texten bör samordnas).
## Problematiska utbildningsplaner

<a class="download-xlsx" href="01-IIT/Analys/Programkurser-olänkade.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (32 rader)</span></a>

> [!example]- 32 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [DITMG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DITMG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Logik och matematik` (7,5hp); rad: - Logik och matematik, 7,5hp |
> | [DITMG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DITMG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `System- och verksamhetsutveckling` ≠ kursplanens namn `System och verksamhetsutveckling` (kurskod `GIK2XZ`); rad: - [[GIK2XZ|System- och verksamhetsutveckling]], 7,5hp |
> | [DSVPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DSVPG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Datakommunikation I` (7,5 hp); rad: - Datakommunikation I, 7,5 hp |
> | [DSVPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DSVPG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Data Storage & Management Technologies` (7,5 hp); rad: - Data Storage & Management Technologies, 7,5 hp |
> | [DSVPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DSVPG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `System- och verksamhetsutveckling` ≠ kursplanens namn `System och verksamhetsutveckling` (kurskod `GIK2XZ`); rad: - [[GIK2XZ|System- och verksamhetsutveckling]], 7,5 hp |
> | [DSVPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DSVPG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Webbaserade geografiska informationssystem` ≠ kursplanens namn `Webbaserade geografiska informationssystem (GIS)` (kurskod `GIK2JX`); rad: - [[GIK2JX|Webbaserade geografiska informationssystem]], 7,5 hp |
> | [KGDWG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=KGDWG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `System- och verksamhetsutveckling` ≠ kursplanens namn `System och verksamhetsutveckling` (kurskod `GIK2XZ`); rad: - [[GIK2XZ|System- och verksamhetsutveckling]], 7,5 hp |
> | [TATPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TATPG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Forskningsmetodik för ingenjörer` (7,5hp); rad: - Forskningsmetodik för ingenjörer, 7,5hp |
> | [TATPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TATPG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Examensarbete i assisterande teknik med inriktning mot maskinteknik` (15 hp); rad: - Examensarbete i assisterande teknik med inriktning mot maskinteknik, 15 hp |
> | [TATPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TATPG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Finita elementmetoden i praktiken` (7,5 hp); rad: - Finita elementmetoden i praktiken, 7,5 hp |
> | [TBTCG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TBTCG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Husbyggnadsprojekt I – Små byggnader och bostadsområden` ≠ kursplanens namn `Husbyggnadsprojekt I - Små byggnader och bostadsområden` (kurskod `GBY2J2`); rad: - [[GBY2J2|Husbyggnadsprojekt I – Små byggnader och bostadsområden]], 15 hp |
> | [TBTCG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TBTCG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Husbyggnadsprojekt III – Byggkonstruktionsprojekt` ≠ kursplanens namn `Husbyggnadsprojekt III - Byggkonstruktionsprojekt` (kurskod `GBY3AX`); rad: - [[GBY3AX|Husbyggnadsprojekt III – Byggkonstruktionsprojekt]], 7,5 hp |
> | [TBTFG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TBTFG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Husbyggnadsprojekt I – små byggnader och bostadsområden` ≠ kursplanens namn `Husbyggnadsprojekt I - Små byggnader och bostadsområden` (kurskod `GBY2J2`); rad: - [[GBY2J2|Husbyggnadsprojekt I – små byggnader och bostadsområden]], 15 hp |
> | [TBYSG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TBYSG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Fysisk planering III – genomförande och planeringsjuridik` (7,5 hp); rad: - Fysisk planering III – genomförande och planeringsjuridik, 7,5 hp |
> | [TBYSG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TBYSG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Husbyggnadsprojekt I – små byggnader och bostadsområden` ≠ kursplanens namn `Husbyggnadsprojekt I - Små byggnader och bostadsområden` (kurskod `GBY2J2`); rad: - [[GBY2J2|Husbyggnadsprojekt I – små byggnader och bostadsområden]], 15 hp |
> | [TEKHG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TEKHG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Industriell ekonomi – grundläggande kurs` ≠ kursplanens namn `Industriell ekonomi - grundläggande kurs` (kurskod `GIE26P`); rad: - [[GIE26P|Industriell ekonomi – grundläggande kurs]], 7,5 hp |
> | [TEKHG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TEKHG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Industriell ekonomi – organisation och ledarskap` ≠ kursplanens namn `Industriell ekonomi - organisation och ledarskap` (kurskod `GIE26M`); rad: - [[GIE26M|Industriell ekonomi – organisation och ledarskap]], 7,5 hp |
> | [TEKHG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TEKHG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Industriell ekonomi – underhåll och kvalitet` ≠ kursplanens namn `Industriell ekonomi - underhåll och kvalitet` (kurskod `GIE26N`); rad: - [[GIE26N|Industriell ekonomi – underhåll och kvalitet]], 7,5 hp |
> | [THIHG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=THIHG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Industriell ekonomi – grundläggande kurs` ≠ kursplanens namn `Industriell ekonomi - grundläggande kurs` (kurskod `GIE26P`); rad: - [[GIE26P|Industriell ekonomi – grundläggande kurs]], 7,5 hp |
> | [THIHG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=THIHG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Utvecklingsprojekt, tillverkning av en solfångare` ≠ kursplanens namn `Utvecklingsprojekt, tillverkning av en solfångare` (kurskod `GEG2JP`); rad: - [[GEG2JP|Utvecklingsprojekt, tillverkning av en solfångare]], 7,5 hp |
> | [TMIEA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TMIEA) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Byggnaders energiprestanda – simulering och analys` ≠ kursplanens namn `Byggnaders energiprestanda - simulering och analys` (kurskod `ABY22W`); rad: - [[ABY22W|Byggnaders energiprestanda – simulering och analys]], 5.0 hp |
> | [TMSSA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TMSSA) | Utbildningsplan | Kursraden ser avbruten/feltrycklig ut | `Solenergiteknikpraktik (7,5 eller` (15 hp); rad: - Solenergiteknikpraktik (7,5 eller, 15 hp |
> | [TMSSA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TMSSA) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Projektkurs 1 – dataanalys för solenergisystem` ≠ kursplanens namn `Projektkurs 1 - dataanalys för solenergisystem` (kurskod `AEG2AK`); rad: - [[AEG2AK|Projektkurs 1 – dataanalys för solenergisystem]], 5 hp |
> | [TMSSA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TMSSA) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Projektkurs 2 – mätsystem` ≠ kursplanens namn `Projektkurs 2 - mätsystem` (kurskod `AEG2AU`); rad: - [[AEG2AU|Projektkurs 2 – mätsystem]], 5 hp |
> | [TMSSA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TMSSA) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Projektkurs 3 – grupprojekt och kommunikation` ≠ kursplanens namn `Projektkurs 3 - grupprojekt och kommunikation` (kurskod `AEG2B5`); rad: - [[AEG2B5|Projektkurs 3 – grupprojekt och kommunikation]], 5 hp |
> | [TPOKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPOKG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Finita elementmetoden` (7,5hp); rad: - Finita elementmetoden, 7,5hp |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `3D CAD grundkurs` (7,5 hp); rad: - 3D CAD grundkurs, 7,5 hp |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Additiv tillverkning` (7,5 hp); rad: - Additiv tillverkning, 7,5 hp |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Examensarbete för högskoleexamen inom maskinteknik` (7,5 hp); rad: - Examensarbete för högskoleexamen inom maskinteknik, 7,5 hp |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Underhåll och kvalitet` (7,5 hp); rad: - Underhåll och kvalitet, 7,5 hp |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `CAM / CNC` ≠ kursplanens namn `CAM/CNC` (kurskod `GMT34P`); rad: - [[GMT34P|CAM / CNC]], 7,5 hp |
> | [TSETA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TSETA) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Design av PV hybrid system` (7,5 hp); rad: - Design av PV hybrid system, 7,5 hp |

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
