---
tags: [analys, programkurser]
up: "[[IHV Analys]]"
status: första pass
---

# Programkurser olänkade

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

En utbildningsplans kurslista (sektionen *Programmets kurser*) bör namnge varje kurs exakt som den heter i kursplanen och länka till den, så att listan går att lita på och navigera. Analysen flaggar två slags avvikelser: kurser vars namn i programtexten inte går att koppla ihop med någon kursplan, och kurser där programtexten syftar på rätt kurs men skriver namnet annorlunda än kursplanens officiella namn. Syftet är att skilja verkliga innehållsfel i utbildningsplanen från rena namnvarianter, så att rätt åtgärd kan vidtas.

Tabellens kolumn **Detalj** visar kursnamnet så som utbildningsplanen skriver det, och **Förslag** den kurs vi bedömer att raden syftar på (med kurskod). Ett `—` i Förslag betyder att ingen kandidat kunnat pekas ut — antingen för att kursen inte finns i Dalarnas katalog, eller för att programtexten är för tvetydig för att peka ut en enskild kurs.

## Metod

Varje utbildningsplans kurslista (sektionen *Programmets kurser*) gås igenom kurs för kurs. Rader som antingen saknar länk till sin kursplan eller vars programtext skiljer sig från kursplanens officiella namn klassas:

| Kategori | Indikator |
|----------|-----------|
| **Okänd kursreferens i program** | Namnet matchar varken en aktiv kursplan eller arkivet över nedlagda kurser |
| **Alternativ-rad (val mellan kurser)** | Raden erbjuder ett val — innehåller *eller*, *alternativt* eller *valbar* |
| **Trunkerad kursrad** | Oavslutad parentes eller ett hängande *eller*/*och*/*,* i radslutet |
| **Programtext skiljer från kursnamn** | Kursen är länkad, men programtextens namn skiljer sig från kursplanens officiella (t.ex. *System- och verksamhetsutveckling* vs *System och verksamhetsutveckling*) |

Kurser som matchar en **nedlagd kursplan** rapporteras separat i [[Nedlagda kursreferenser]] och tas inte upp här.

## Datakälla

- Samtliga utbildningsplaner vid Högskolan Dalarna.
- Aktiva kursnamn och kurskoder från kursplanerna.
- Förteckningen över nedlagda kurser på du.se.

## Rekommendationer

1. **Okänd kursreferens i program** är ett innehållsfel i utbildningsplanen — kursnamnet stämmer inte mot Dalarnas katalog. Möjliga orsaker: stavfel, kursen aldrig publicerad på du.se, eller felaktig benämning. Lyft till programansvarig.
2. **Alternativ-rad** är legitim — programmet låter studenten välja mellan kurser. Ingen åtgärd behövs om raden är välformulerad.
3. **Trunkerad kursrad** är oftast en avbruten mening i den ursprungliga programtexten. Granska den rapporterade raden mot du.se.
4. **Programtext skiljer från kursnamn** kräver att programansvarig uppdaterar kurslistan i utbildningsplanen så att texten matchar kursplanens officiella namn. Vanligaste orsaken är att programtexten drar ihop två namn (*X- och Y* istället för *X och Y*).
5. **Förslagskolumnen är ett underlag, inte ett beslut.** Kontrollera kurskoden mot du.se innan programtexten rättas — särskilt när flera kurser delar snarlika namn (t.ex. *… åk 7–9* vs *… gymnasieskolan*).
6. **Rader utan förslag är oftast inte namnfel.** Tre återkommande orsaker, som alla kräver dialog med programansvarig snarare än en texträttning:
    - *Kursplanen är ännu inte fastställd* — nya program hinner före sina kurser. SPARG (fastställd 2025-04-16) har hela år 1 länkat och år 2–3 helt olänkat.
    - *Kursen publicerades aldrig som egen kursplan* — temakurserna i HAFSA och kurserna i KMLJG finns varken aktivt eller bland de nedlagda kurserna.
    - *Raden är en delkurs, inte en kurs* — SSHVG:s sociologirader är innehåll i 30 hp-kurserna [[GSO2XU]] och [[GSO2XV]], inte egna kursplaner.
7. **Rena rubrikrader tas inte upp.** Rader som *Inriktning sociologi II, 30 hp* namnger ett block vars ingående kurser listas som egna rader under det, och rapporteras därför inte.
