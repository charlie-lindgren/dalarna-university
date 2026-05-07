---
tags: [analys, oversattning]
up: "[[IIT MOC]]"
status: första pass
---

# Samstämmighet svenska och engelska

## Problematiska kursplaner

<a class="download-xlsx" href="Samstämmighet-svenska-och-engelska.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (8 rader)</span></a>

> [!example]- 8 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [AMD238](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMD238) | MDI | Paritetsskillnad | Svenska: 17 mål, engelska: 0 mål (diff 17) |
> | [AMD239](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMD239) | MDI | Paritetsskillnad | Svenska: 17 mål, engelska: 0 mål (diff 17) |
> | [GMD2AR](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2AR) | MDI | Paritetsskillnad | Svenska: 28 mål, engelska: 0 mål (diff 28) |
> | [GMD2GG](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2GG) | MDI | Paritetsskillnad | Svenska: 24 mål, engelska: 1 mål (diff 23) |
> | [GMD2MH](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2MH) | MDI | Paritetsskillnad | Svenska: 10 mål, engelska: 0 mål (diff 10) |
> | [GMD2TV](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2TV) | MDI | Paritetsskillnad | Svenska: 32 mål, engelska: 0 mål (diff 32) |
> | [MT1033](https://www.du.se/sv/utbildning/kurser/kursplan/?code=MT1033) | MTA | Paritetsskillnad | Svenska: 1 mål, engelska: 0 mål (diff 1) |
> | [ST1013](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ST1013) | STA | Paritetsskillnad | Svenska: 8 mål, engelska: 0 mål (diff 8) |

## Syfte

Kursplaner med både svensk och engelsk version bör ha **samma antal lärandemål och samma struktur** i båda språken. När en översättning saknar lärandemål eller utökar med fler riskerar de att avvika i sak — vilket är ett formellt problem för internationella studenter.

## Metod

`qa/check_kursplaner.py` jämför antalet bullets i sektionen `## Lärandemål` mot `## Learning Outcomes` och flaggar filer där absolutdifferensen överstiger 3.

**Begränsningar:**

- Endast bullet-räkning. Översättningens **kvalitet** (terminologi, stilistik, exakthet) kan inte mätas automatiskt.
- Om ett språk har sammanslagna bullets ("a, b, samt c" i en bullet) medan det andra har separata, flaggas det fastän sak-innehållet är detsamma.
- Filer som saknar engelsk version helt utelämnas (legitimt — inte alla kurser ges på engelska).

Denna analys är **manuellt kurerad** — automatisk paritetsmätning ger en startpunkt, men slutbedömningen kräver att en granskare läser båda versionerna parallellt.

## Datakälla

- Kursplaner under `0X {INST}/Kursplaner/` som har **både** `## Lärandemål` och `## Learning Outcomes`
- Tröskel: |sv − en| > 3 bullets

## Resultat

*Fylls i efter första genomgång.*

## Observationer

*Fylls i efter första genomgång.*

## Rekommendationer

1. **Granska varje flaggad kursplan** med båda språkversionerna parallellt.
2. **Synkronisera bullets** vid nästa revision om innehållet faktiskt är detsamma.
3. **Om sak-innehållet skiljer sig:** välj en kanonisk version och uppdatera den andra. Dokumentera i ärendebeskrivningen vilken version som var ledande.
