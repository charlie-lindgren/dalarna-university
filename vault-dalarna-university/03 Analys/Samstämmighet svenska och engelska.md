---
tags: [analys, oversattning]
up: "[[Analys MOC]]"
status: första pass
---

# Samstämmighet svenska och engelska

## Problematiska kursplaner

> [!example]- 0 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |

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

- Kursplaner under `01 Kursplaner/` som har **både** `## Lärandemål` och `## Learning Outcomes`
- Tröskel: |sv − en| > 3 bullets

## Resultat

*Fylls i efter första genomgång.*

## Observationer

*Fylls i efter första genomgång.*

## Rekommendationer

1. **Granska varje flaggad kursplan** med båda språkversionerna parallellt.
2. **Synkronisera bullets** vid nästa revision om innehållet faktiskt är detsamma.
3. **Om sak-innehållet skiljer sig:** välj en kanonisk version och uppdatera den andra. Dokumentera i ärendebeskrivningen vilken version som var ledande.
