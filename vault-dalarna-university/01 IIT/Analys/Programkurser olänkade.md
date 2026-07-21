---
tags: [analys, programkurser]
up: "[[IIT Analys]]"
status: första pass
---

# Programkurser olänkade

## Bakgrund

Utbildningsplanens `## 3. Programmets kurser`-sektion ska helst lista varje kurs som en wikilänk till motsvarande kursplansfil (`[[KOD|Namn]], hp`). Analysen flaggar två typer av problem: **olänkade bullets** (där länken saknas helt) och **länkade bullets där programtexten avviker från kursplanens kanoniska namn** (vår skrapa hittar fortfarande rätt kurs via normalisering, men texten bör samordnas).

Tabellen delar upp fyndet i två kolumner: **Detalj** är kursnamnet så som utbildningsplanen skriver det, **Förslag** är den kurs vi bedömer att raden syftar på (med kurskod). Rader med `—` i Förslag saknar ännu en kandidat — antingen för att kursen verkligen inte finns i HDa:s katalog, eller för att programtexten är för tvetydig för att peka ut en enskild kurs. Förslagen kommer från en handkurerad mappning i [qa/checks_nedlagda.py](../../qa/checks_nedlagda.py) (`_KANDIDAT_MATCHNINGAR_RAW`) och kan fyllas på efter hand.

## Problematiska utbildningsplaner

<a class="download-xlsx" href="01-IIT/Analys/Programkurser-olänkade.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (16 rader)</span></a>

> [!example]- 16 fynd — klicka för att expandera
>
> | Kursplan | Sida | Ämne | Fastställd | Reviderad | Problem | Detalj | Förslag |
> | --- | --- | --- | --- | --- | --- | --- | --- |
> | [DITMG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DITMG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/DITMG">sida</a> | Utbildningsplan | 2019-03-05 | 2023-08-30 | Programtext avviker från kursplanens namn | `Logik och matematik` (7,5hp) | `Logik och matematik för datavetenskap` (kurskod `GMI23G`) |
> | [DITMG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DITMG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/DITMG">sida</a> | Utbildningsplan | 2019-03-05 | 2023-08-30 | Programtext avviker från kursplanens namn | `System- och verksamhetsutveckling` | `System och verksamhetsutveckling` (kurskod `GIK2XZ`) |
> | [DSVPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DSVPG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/DSVPG">sida</a> | Utbildningsplan | 2019-03-05 | — | Kurs finns aktivt men scrapern länkade inte | `Datakommunikation I` (7,5 hp) | `Datakommunikation 1` (kurskod `GDT2JM`) |
> | [DSVPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DSVPG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/DSVPG">sida</a> | Utbildningsplan | 2019-03-05 | — | Programtext avviker från kursplanens namn | `Data Storage & Management Technologies` (7,5 hp) | `Data Storage and Management Technologies` (kurskod `GIK2NV`) |
> | [DSVPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DSVPG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/DSVPG">sida</a> | Utbildningsplan | 2019-03-05 | — | Programtext avviker från kursplanens namn | `System- och verksamhetsutveckling` | `System och verksamhetsutveckling` (kurskod `GIK2XZ`) |
> | [DSVPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=DSVPG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/DSVPG">sida</a> | Utbildningsplan | 2019-03-05 | — | Programtext avviker från kursplanens namn | `Webbaserade geografiska informationssystem` | `Webbaserade geografiska informationssystem (GIS)` (kurskod `GIK2JX`) |
> | [KGDWG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=KGDWG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/KGDWG">sida</a> | Utbildningsplan | 2021-10-08 | — | Programtext avviker från kursplanens namn | `System- och verksamhetsutveckling` | `System och verksamhetsutveckling` (kurskod `GIK2XZ`) |
> | [TATPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TATPG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TATPG">sida</a> | Utbildningsplan | 2025-12-19 | — | Programtext avviker från kursplanens namn | `Finita elementmetoden i praktiken` (7,5 hp) | `Finita element metoden i praktiken` (kurskod `GMT2QF`) |
> | [TBYSG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TBYSG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TBYSG">sida</a> | Utbildningsplan | 2019-12-18 | 2020-11-25 | Programtext avviker från kursplanens namn | `Fysisk planering III – genomförande och planeringsjuridik` (7,5 hp) | `Fysisk planering III - genomförande och juridisk fördjupning` (kurskod `GSQ2PH`) |
> | [TPOKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPOKG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TPOKG">sida</a> | Utbildningsplan | 2019-02-01 | 2021-12-15 | Programtext avviker från kursplanens namn | `Finita elementmetoden` (7,5hp) | `Finita element metoden i praktiken` (kurskod `GMT2QF`) |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TPTAG">sida</a> | Utbildningsplan | 2023-03-28 | — | Programtext avviker från kursplanens namn | `3D CAD grundkurs` (7,5 hp) | `3D-CAD – grundkurs` (kurskod `GMT338`) |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TPTAG">sida</a> | Utbildningsplan | 2023-03-28 | — | Programtext avviker från kursplanens namn | `Additiv tillverkning` (7,5 hp) | `Additiv tillverkning (3D printing)` (kurskod `GMT34A`) |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TPTAG">sida</a> | Utbildningsplan | 2023-03-28 | — | Programtext avviker från kursplanens namn | `Examensarbete för högskoleexamen inom maskinteknik` (7,5 hp) | `Examensarbete för högskoleexamen i maskinteknik` (kurskod `GMT34W`) |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TPTAG">sida</a> | Utbildningsplan | 2023-03-28 | — | Programtext avviker från kursplanens namn | `Underhåll och kvalitet` (7,5 hp) | `Industriell ekonomi - underhåll och kvalitet` (kurskod `GIE26N`) |
> | [TPTAG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TPTAG) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TPTAG">sida</a> | Utbildningsplan | 2023-03-28 | — | Programtext avviker från kursplanens namn | `CAM / CNC` | `CAM/CNC` (kurskod `GMT34P`) |
> | [TSETA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=TSETA) | <a class="no-graph" href="01-IIT/Utbildningsplaner/TSETA">sida</a> | Utbildningsplan | 2015-10-07 | 2023-05-30 | Programtext avviker från kursplanens namn | `Design av PV hybrid system` (7,5 hp) | `Design av PV- och hybridsystem` (kurskod `AEG26X`) |

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
6. **Förslagskolumnen är ett underlag, inte ett beslut.** Kontrollera kurskoden mot du.se innan programtexten rättas — särskilt när flera kurser delar snarlika namn (t.ex. `… åk 7-9` vs `… gymnasieskolan`). Programspecifika fall ligger i `_KANDIDAT_MATCHNINGAR_PROG_RAW`, nycklade på (programkod, text), just för att samma rad kan betyda olika kurser i olika program.
7. **Rader utan förslag är oftast inte namnfel.** Tre återkommande orsaker, som alla kräver dialog med programansvarig snarare än en texträttning:
    - *Kursplanen är ännu inte fastställd* — nya program hinner före sina kurser. SPARG (fastställd 2025-04-16) har hela år 1 länkat och år 2–3 helt olänkat.
    - *Kursen publicerades aldrig som egen kursplan* — temakurserna i HAFSA och kurserna i KMLJG finns varken aktivt eller i nedlagda-arkivet.
    - *Raden är en delkurs, inte en kurs* — SSHVG:s sociologirader är innehåll i 30 hp-kurserna [[GSO2XU]] och [[GSO2XV]], inte egna kursplaner.
8. **Rena rubrikrader filtreras bort.** Rader som `Inriktning sociologi II, 30 hp` namnger ett block vars ingående kurser listas som egna bullets under det; de ligger i `_BULLET_EXKLUDERAD` och rapporteras inte alls.
