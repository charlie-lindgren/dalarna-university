---
tags: [analys, programkurser]
up: "[[IHV Analys MOC]]"
status: första pass
---

# Programkurser olänkade

## Bakgrund

Utbildningsplanens `## 3. Programmets kurser`-sektion ska helst lista varje kurs som en wikilänk till motsvarande kursplansfil (`[[KOD|Namn]], hp`). Analysen flaggar två typer av problem: **olänkade bullets** (där länken saknas helt) och **länkade bullets där programtexten avviker från kursplanens kanoniska namn** (vår skrapa hittar fortfarande rätt kurs via normalisering, men texten bör samordnas).
## Problematiska utbildningsplaner

<a class="download-xlsx" href="02-IHV/Analys/Programkurser-olänkade.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (18 rader)</span></a>

> [!example]- 18 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [VBSKA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VBSKA) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Gravididet, förlossning och postpartumvård 1` (7,5 hp); rad: - Gravididet, förlossning och postpartumvård 1, 7,5 hp |
> | [VBSKA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VBSKA) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Gravididet, förlossning och postpartumvård 2` (6 hp); rad: - Gravididet, förlossning och postpartumvård 2, 6 hp |
> | [VBSKA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VBSKA) | Utbildningsplan | Kursraden ser avbruten/feltrycklig ut | `) kurser som krävs för magisterexamen` (60 hp); rad: - ) kurser som krävs för magisterexamen, 60 hp |
> | [VGSEA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VGSEA) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Strategier för implementering av förbättringsarbete i hälso-sjukvård` (7,5 hp); rad: - Strategier för implementering av förbättringsarbete i hälso-sjukvård, 7,5 hp |
> | [VIDRG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VIDRG) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Media och kommunikation inom idrott` (7,5hp); rad: - Media och kommunikation inom idrott, 7,5hp |
> | [VSADA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSADA) | Utbildningsplan | Kursnamnet finns varken aktivt eller nedlagt | `Personcentrerad vård av personer med demens` (7,5 hp); rad: - Personcentrerad vård av personer med demens, 7,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Metoder för evidensbaserad vård I - Huvudområde Omvårdnad` ≠ kursplanens namn `Metoder för evidensbaserad vård I` (kurskod `GVÅ2N9`); rad: - [[GVÅ2N9|Metoder för evidensbaserad vård I - Huvudområde Omvårdnad]], 7,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Människans grundläggande omvårdnadsbehov - Huvudområde Omvårdnad` ≠ kursplanens namn `Människans grundläggande omvårdnadsbehov` (kurskod `GVÅ2RA`); rad: - [[GVÅ2RA|Människans grundläggande omvårdnadsbehov - Huvudområde Omvårdnad]], 10,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Människa, hälsa och samhälle - Huvudområde Omvårdnad` ≠ kursplanens namn `Människa, hälsa och samhälle` (kurskod `GVÅ2AP`); rad: - [[GVÅ2AP|Människa, hälsa och samhälle - Huvudområde Omvårdnad]], 7,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Metoder och teorier vid symtom och tecken på hälsa/ohälsa I - Huvudområde Omvårdnad` ≠ kursplanens namn `Metoder och teorier vid symtom och tecken på hälsa/ohälsa I` (kurskod `VÅ1053`); rad: - [[VÅ1053|Metoder och teorier vid symtom och tecken på hälsa/ohälsa I - Huvudområde Omvårdnad]], 30 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Personcentrerad vård inom somatisk vård - Huvudområde Omvårdnad` ≠ kursplanens namn `Personcentrerad vård inom somatisk vård` (kurskod `GVÅ384`); rad: - [[GVÅ384|Personcentrerad vård inom somatisk vård - Huvudområde Omvårdnad]], 15 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Metoder och teorier vid symtom och tecken på hälsa/ohälsa II - Huvudområde Omvårdnad` ≠ kursplanens namn `Metoder och teorier vid symtom och tecken på hälsa/ohälsa II` (kurskod `GVÅ37Y`); rad: - [[GVÅ37Y|Metoder och teorier vid symtom och tecken på hälsa/ohälsa II - Huvudområde Omvårdnad]], 7,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Ledarskap och teamarbete - Huvudområde Omvårdnad` ≠ kursplanens namn `Ledarskap och teamarbete` (kurskod `GVÅ2S3`); rad: - [[GVÅ2S3|Ledarskap och teamarbete - Huvudområde Omvårdnad]], 7,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Personcentrerad vård inom olika vårdsammanhang - Huvudområde Omvårdnad` ≠ kursplanens namn `Personcentrerad vård inom olika vårdsammanhang` (kurskod `GVÅ2H6`); rad: - [[GVÅ2H6|Personcentrerad vård inom olika vårdsammanhang - Huvudområde Omvårdnad]], 22,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Personcentrerad vård inom psykiatrisk vård - Huvudområde Omvårdnad` ≠ kursplanens namn `Personcentrerad vård inom psykiatrisk vård` (kurskod `GVÅ2HM`); rad: - [[GVÅ2HM|Personcentrerad vård inom psykiatrisk vård - Huvudområde Omvårdnad]], 7,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Metoder för evidensbaserad vård II - Huvudområde Omvårdnad` ≠ kursplanens namn `Metoder för evidensbaserad vård II` (kurskod `GVÅ2ZY`); rad: - [[GVÅ2ZY|Metoder för evidensbaserad vård II - Huvudområde Omvårdnad]], 7,5 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Examensarbete i omvårdnad - Huvudområde Omvårdnad` ≠ kursplanens namn `Examensarbete i omvårdnad` (kurskod `GVÅ36W`); rad: - [[GVÅ36W|Examensarbete i omvårdnad - Huvudområde Omvårdnad]], 15 hp |
> | [VSSKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=VSSKG) | Utbildningsplan | Programtext avviker från kursplanens namn | Programtext `Personcentrerad vård med fördjupning inom omvårdnad - Huvudområde Omvårdnad` ≠ kursplanens namn `Personcentrerad vård med fördjupning inom omvårdnad` (kurskod `GVÅ2ZG`); rad: - [[GVÅ2ZG|Personcentrerad vård med fördjupning inom omvårdnad - Huvudområde Omvårdnad]], 7,5 hp |

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
