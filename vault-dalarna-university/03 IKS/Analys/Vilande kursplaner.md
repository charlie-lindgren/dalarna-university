---
tags: [analys, kurslivscykel, vilande]
up: "[[IKS MOC]]"
status: första pass
---

# Vilande kursplaner

## Problematiska kursplaner

<a class="download-xlsx" href="Vilande-kursplaner.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (7 rader)</span></a>

> [!example]- 7 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Institution | Fastställd | Problem |
> | --- | --- | --- | --- | --- |
> | [AHI29Q](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AHI29Q) | HIA | IKS | 2023-10-05 | Ingen aktiv kursomgång hittad på kurssidan |
> | [AHI29R](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AHI29R) | HIA | IKS | 2023-10-05 | Ingen aktiv kursomgång hittad på kurssidan |
> | [GFI37Z](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GFI37Z) | FIA | IKS | 2023-12-07 | Ingen aktiv kursomgång hittad på kurssidan |
> | [GPG3CN](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GPG3CN) | PGA | IKS | 2024-09-05 | Ingen aktiv kursomgång hittad på kurssidan |
> | [GHI3CP](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GHI3CP) | HIA | IKS | 2024-09-27 | Ingen aktiv kursomgång hittad på kurssidan |
> | [GRK3CQ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GRK3CQ) | RKA | IKS | 2024-09-27 | Ingen aktiv kursomgång hittad på kurssidan |
> | [APG2CC](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG2CC) | PGA | IKS | 2026-02-23 | Ingen aktiv kursomgång hittad på kurssidan |

## Syfte

Identifiera kurser som är **vilande**: de saknar synlig aktiv kursomgång på kurssidan på du.se. Det är ofta legitimt, men signalen kan också tyda på att utfasning eller arkivering inte genomförts klart.

## Metod

1. Läs in aktuellt kursutbud per ämne från du.se (sök/listning).
2. Jämför mot kurskoder som finns i vaulten.
3. För koder som saknas i aktuellt utbud: kontrollera direkt kursplans-URL.
4. Markera som **vilande** när ingen aktiv kursomgång ("Start vecka") hittas.

**Begränsningar:**

- En vilande kurs är inte automatiskt ett fel; analysen visar främst uppföljningsbehov.
- Om du.se tillfälligt svarar fel kan klassningen bli osäker tills nästa körning.

## Datakälla

- `qa/identify_ej_aktiv.py`
- Kursutbudslistning + kursplanssidor på du.se
- Kursplansfiler under `0X {INST}/Kursplaner/`

## Resultat

*Fylls i efter genomgång.*

## Observationer

*Fylls i efter genomgång.*

## Rekommendationer

1. Bekräfta med ämnesföreträdare om varje vilande kurs ska återaktiveras, kvarstå eller avvecklas.
2. För kurser som ska avvecklas: planera flytt till ej-aktiv eller annan tydlig arkiveringsstatus.
3. Kör analysen regelbundet för att upptäcka glidning mellan utbud och publicerade kursplaner.
