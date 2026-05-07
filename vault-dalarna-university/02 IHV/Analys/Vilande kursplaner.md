---
tags: [analys, kurslivscykel, vilande]
up: "[[IHV MOC]]"
status: första pass
---

# Vilande kursplaner

## Problematiska kursplaner

<a class="download-xlsx" href="Vilande-kursplaner.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (1 rader)</span></a>

> [!example]- 1 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Institution | Fastställd | Problem |
> | --- | --- | --- | --- | --- |
> | [GIH3AQ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH3AQ) | IDA | IHV | 2024-02-27 | Ingen aktiv kursomgång hittad på kurssidan |

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
