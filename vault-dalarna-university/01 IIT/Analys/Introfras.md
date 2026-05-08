---
tags: [analys, sprak]
up: "[[IIT MOC]]"
status: första pass
---

# Introfras

## Problematiska kursplaner

<a class="download-xlsx" href="01-IIT/Analys/Introfras.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (0 rader)</span></a>

> [!example]- 0 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |

## Syfte

Lärandemålen i en kursplan ska föregås av en introfras som signalerar att det följer en uppräkning av mål — t.ex. *"Efter godkänd kurs ska studenten kunna:"*. När frasen helt saknas blir det otydligt för studenten *vilka* förmågor som faktiskt utvärderas, och automatisk extraktion av mål blir omöjlig. Syftet är att kartlägga **hur många kursplaner som helt saknar introfras** vid Högskolan Dalarna och om problemet är systematiskt inom vissa ämnen eller institutioner.

## Metod

`qa/check_kursplaner.py` flaggar tre tomhetsfall under check-id `introfras-saknas`:

- Hela `## Lärandemål`-sektionen saknas.
- Sektionen finns men utan punktlista.
- Sektionen och punktlistan finns men ingen igenkännbar fras (*"Efter ... kunna"*, *"studenten ska ... kunna"*, *"kursens mål"* m.fl.) före första punkten.

Frasens **exakta formulering** granskas inte här — det hanteras av [[Frasningskonsistens]].

## Datakälla

- Alla kursplaner under `0X {INST}/Kursplaner/`
- Endast den svenska sektionen (`## Lärandemål`)
- Tidpunkt: senast skrapade datum, se [[Dalarna Dashboard]]

## Resultat

*Fylls i efter första genomgång — se tabellen ovan för rådata från senaste QA-körningen.*

## Observationer

*Fylls i efter första genomgång.*

## Rekommendationer

1. **Inför introfras** i alla kursplaner — minst en mening som ramar in punktlistan.
2. **Använd gold standard-formuleringen** *"Efter godkänd kurs ska studenten kunna:"* när den passar (se [[Frasningskonsistens]] för konsistensanalysen).
3. **Lyft frågan i berörda kvalitetsutskott** — saknad introfras kan tyda på att kursplanen aldrig granskats redaktionellt.
