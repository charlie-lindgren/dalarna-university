---
aliases: [Analys, Analyser]
tags: [MOC, analys]
cssclasses: [wide-page]
up: "[[Dalarna Dashboard]]"
---

# Analys — Holistisk kvalitetsbedömning

> [!abstract] Syfte
> Granska kvalitet och samstämmighet **tvärs** alla befintliga kursplaner och utbildningsplaner vid Högskolan Dalarna — IIT, IHV, IKS och ISLL. Den ärendebaserade granskning som UKU och motsvarande kvalitetsutskott normalt utför ser en plan i taget; dessa analyser ser hela mängden samtidigt.

## Översikt

Varje analys följer samma mall:

1. **Syfte** — vad vi vill veta och varför det är värt att veta.
2. **Metod** — hur datat samlats in (regex, manuell läsning, taxonomi-kodning, etc.) och vilka begränsningar metoden har.
3. **Datakälla** — vilka filer eller fält som ingick.
4. **Resultat** — kvantitativ bild (frekvenser, distributioner).
5. **Observationer** — kvalitativa tolkningar av resultatet.
6. **Rekommendationer** — vad institutionerna kan göra åt det.

## Pågående analyser

> [!example] Språk & form
>
> - [[Frasningskonsistens lärandemål]] — Variation i den standardiserade introfrasen
> - [[Stavfel och språkbruk]] — Stavfel, dubbletter, mellanrumsfel
> - [[Samstämmighet svenska och engelska]] — Översättningskvalitet och paritet

<!-- -->

> [!example] Pedagogik
>
> - [[Bloom-taxonomi]] — Verbnivåer i lärandemål, alignment med kursnivå
> - [[Omfång på lärandemål]] — Antal lärandemål, ord per mål, granularitet

<!-- -->

> [!example] Examination & betyg
>
> - [[Examinationsformer]] — Variation i examinationsformer per ämne och nivå
> - [[Betygsskalor]] — Användning av U–G vs U–VG, distribution och motivering

<!-- -->

> [!example] Kurslivscykel
>
> - [[Vilande kursplaner]] — Kurser med publicerad kursplan men utan aktuellt utbud

<!-- -->

## Status

| Analys                                     | Status      |
| ------------------------------------------ | ----------- |
| Frasningskonsistens lärandemål             | Första pass |
| Stavfel och språkbruk                      | Första pass |
| Bloom-taxonomi                             | Första pass |
| Betygsskalor                               | Första pass |
| Examinationsformer                         | Första pass |
| Omfång på lärandemål                       | Första pass |
| Samstämmighet svenska och engelska         | Första pass |
| Vilande kursplaner                         | Första pass |

## Pipeline

Analyserna fylls automatiskt från QA-rapporter genererade av `qa/check_kursplaner.py`. Se [[Dalarna Dashboard]] eller projektets `CLAUDE.md` för körningsinstruktioner.
