---
tags: [analys, sprak]
up: "[[IHV Analys]]"
status: första pass
---

# Stavfel och språkbruk

## Problematiska kursplaner

<a class="download-xlsx" href="02-IHV/Analys/Stavfel-och-språkbruk.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (5 rader)</span></a>

> [!example]- 5 fynd — klicka för att expandera
>
> | Kursplan | Sida | Ämne | Fastställd | Reviderad | Problem | Detalj |
> | --- | --- | --- | --- | --- | --- | --- |
> | [GIH334](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH334) | <a class="no-graph" href="02-IHV/Kursplaner/IDA/GIH334">sida</a> | IDA | 2023-02-07 | — | Felstavning (en) | `collaboratation` (en) |
> | [GSA2XN](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA2XN) | <a class="no-graph" href="02-IHV/Kursplaner/SAA/GSA2XN">sida</a> | SAA | 2022-09-08 | — | Felstavning (en) | `guidlines` (en) |
> | [SA2020](https://www.du.se/sv/utbildning/kurser/kursplan/?code=SA2020) | <a class="no-graph" href="02-IHV/Kursplaner/SAA/SA2020">sida</a> | SAA | 2014-12-23 | — | Felstavning | `fördjuping` (sv) |
> | [ASR22N](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ASR22N) | <a class="no-graph" href="02-IHV/Kursplaner/SRP/ASR22N">sida</a> | SRP | 2018-12-06 | — | Felstavning (en) | `ethtical` (en) |
> | [GSR2A5](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSR2A5) | <a class="no-graph" href="02-IHV/Kursplaner/SRP/GSR2A5">sida</a> | SRP | 2019-06-19 | 2021-02-19 | Felstavning (en) | `adolscents` (en) |

## Syfte

Identifiera **uppenbara skrivfel** (dubblerade ord, kända felstavningar, ord som inte finns i ordboken) i kursplaner tvärs Högskolan Dalarnas fyra institutioner. Stavfel skadar inte bara läsningen utan undergräver intrycket av kvalitetsstyrning.

## Metod

Fyra kontroller körs per kursplan:

1. **Dubblerade ord** — t.ex. *modeller modeller* — med undantag för legitima upprepningar (*för för*, *och och*).
2. **Kända felstavningar** — en kurerad lista över återkommande typos i svensk respektive engelsk text. Varje fynd visar både den felaktiga formen och föreslagen rättning.
3. **Stavningskontroll på svenska** — flagga ord som inte finns i svenska ordboken och som förekommer i färre än fyra kursplaner (sällsynta ord = sannolikare typo, vanliga ord = sannolikare domänterm).
4. **Stavningskontroll på engelska** — samma logik mot den engelska versionen, tröskel < 5 kursplaner.

Båda stavningskontrollerna filtreras mot omfattande ignorelistor (domäntermer, akronymer, brittiska stavningar) som underhålls och utökas iterativt.

**Begränsningar:** Stavningskontrollen missar kontextberoende fel (*var/vart*, *de/dem*). Egennamn och facktermer kan ge falska träffar tills de adderas till ignorelistan.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna (IIT, IHV, IKS, ISLL).
- Svensk text: kursplanens brödtext exklusive avsnittet `English Version`.
- Engelsk text: enbart avsnittet `English Version`.

## Rekommendationer

1. **Korrigera bekräftade stavfel** vid nästa revision av respektive kursplan.
2. **Verifiera ord som ser hopskrivna ut** (t.ex. *shouldbe*, *buildingprocess*) genom att jämföra mot källan på du.se — de uppstår ibland när text kopierats utan korrekta mellanslag.
3. **Kör analysen regelbundet** så att nya kursplaner fångas tidigt.
