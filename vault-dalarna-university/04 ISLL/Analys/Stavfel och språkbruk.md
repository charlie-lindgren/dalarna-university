---
tags: [analys, sprak]
up: "[[ISLL Analys MOC]]"
status: första pass
---

# Stavfel och språkbruk

## Problematiska kursplaner

<a class="download-xlsx" href="04-ISLL/Analys/Stavfel-och-språkbruk.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (5 rader)</span></a>

> [!example]- 5 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [AR2001](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AR2001) | ARA | Dubblerat ord | `the` — …resentations of varying length.  \### Assessment  Grades for the the _Grammar and Texts_ module are based on continuous assesmen… |
> | [GFR2A8](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GFR2A8) | FRA | Dubblerat ord | `writing` — …y basic French grammar in their own text production such as writing writing simple texts or summarizing a newspaper article in good Fre… |
> | [GKI3CB](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GKI3CB) | KIA | Dubblerat ord | `and` — …cate unhindered in Chinese on a variety of topics    - read and and understand short authentic Chinese texts    - compose short… |
> | [KI1030](https://www.du.se/sv/utbildning/kurser/kursplan/?code=KI1030) | KIA | Dubblerat ord | `and` — …s such as education, sports, and environment etc.    - read and and comprehend short authentic Chinese texts    - compose short… |
> | [GPR2W2](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GPR2W2) | PRA | Dubblerat ord | `languages` — …cific context and to analyse the dynamics between different languages languages and linguistic varieties from a societal perspective. In th… |

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
