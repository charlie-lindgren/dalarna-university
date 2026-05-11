---
tags: [analys, oversattning]
up: "[[IIT MOC]]"
status: första pass
---

# Samstämmighet svenska och engelska

## Problematiska kursplaner

<a class="download-xlsx" href="01-IIT/Analys/Samstämmighet-svenska-och-engelska.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (17 rader)</span></a>

> [!example]- 17 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [IK1064](https://www.du.se/sv/utbildning/kurser/kursplan/?code=IK1064) | IKA | Paritetsskillnad | Svenska: 12 mål, engelska: 0 mål (diff 12) |
> | [AMD238](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMD238) | MDI | Paritetsskillnad | Svenska: 17 mål, engelska: 0 mål (diff 17) |
> | [AMD239](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMD239) | MDI | Paritetsskillnad | Svenska: 17 mål, engelska: 0 mål (diff 17) |
> | [GMD2AR](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2AR) | MDI | Paritetsskillnad | Svenska: 28 mål, engelska: 0 mål (diff 28) |
> | [GMD2GF](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2GF) | MDI | Paritetsskillnad | Svenska: 24 mål, engelska: 1 mål (diff 23) |
> | [GMD2GG](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2GG) | MDI | Paritetsskillnad | Svenska: 24 mål, engelska: 1 mål (diff 23) |
> | [GMD2H3](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2H3) | MDI | Paritetsskillnad | Svenska: 8 mål, engelska: 0 mål (diff 8) |
> | [GMD2MH](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2MH) | MDI | Paritetsskillnad | Svenska: 10 mål, engelska: 0 mål (diff 10) |
> | [GMD2TV](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2TV) | MDI | Paritetsskillnad | Svenska: 32 mål, engelska: 0 mål (diff 32) |
> | [GMD2XQ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2XQ) | MDI | Paritetsskillnad | Svenska: 77 mål, engelska: 0 mål (diff 77) |
> | [GMD33X](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD33X) | MDI | Paritetsskillnad | Svenska: 45 mål, engelska: 0 mål (diff 45) |
> | [GMD33Y](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD33Y) | MDI | Paritetsskillnad | Svenska: 77 mål, engelska: 0 mål (diff 77) |
> | [MT1033](https://www.du.se/sv/utbildning/kurser/kursplan/?code=MT1033) | MTA | Paritetsskillnad | Svenska: 1 mål, engelska: 0 mål (diff 1) |
> | [MT1060](https://www.du.se/sv/utbildning/kurser/kursplan/?code=MT1060) | MTA | Paritetsskillnad | Svenska: 10 mål, engelska: 9 mål (diff 1) |
> | [MT2006](https://www.du.se/sv/utbildning/kurser/kursplan/?code=MT2006) | MTA | Paritetsskillnad | Svenska: 3 mål, engelska: 0 mål (diff 3) |
> | [GSQ23K](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ23K) | SQQ | Paritetsskillnad | Svenska: 5 mål, engelska: 4 mål (diff 1) |
> | [ST1013](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ST1013) | STA | Paritetsskillnad | Svenska: 8 mål, engelska: 0 mål (diff 8) |

## Syfte

Kursplaner med både svensk och engelsk version bör ha **samma antal lärandemål och samma struktur** i båda språken. När en översättning saknar lärandemål eller utökar med fler riskerar de att avvika i sak — vilket är ett formellt problem för internationella studenter.

## Metod

Antalet punkter i sektionen `Lärandemål` jämförs med antalet i `Learning Outcomes`. Varje kursplan där antalet skiljer sig (med minst en) flaggas. Antalet lärandemål ska vara identiskt mellan språken.

**Begränsningar:**

- Endast antalsjämförelse. Översättningens **kvalitet** (terminologi, stilistik, exakthet) kan inte mätas automatiskt.
- Om ett språk har sammanslagna punkter (*"a, b, samt c"* i en punkt) medan det andra har separata, flaggas det fastän sak-innehållet är detsamma.
- Kursplaner som saknar engelsk version helt utelämnas (legitimt — inte alla kurser ges på engelska).

Listan ska användas som diskussionsunderlag. Slutbedömningen kräver att en granskare läser båda versionerna parallellt.

## Datakälla

- Kursplaner från du.se vid Högskolan Dalarna som har **både** svensk och engelsk version av lärandemålen.
- Tröskel: skillnad ≥ 1 mellan språken (alla diskrepanser flaggas).

## Rekommendationer

1. **Granska varje flaggad kursplan** med båda språkversionerna parallellt.
2. **Synkronisera punkterna** vid nästa revision om innehållet faktiskt är detsamma.
3. **Om sak-innehållet skiljer sig:** välj en kanonisk version och uppdatera den andra. Dokumentera vilken version som var ledande.
