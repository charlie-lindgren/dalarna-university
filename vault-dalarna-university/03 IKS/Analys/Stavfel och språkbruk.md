---
tags: [analys, sprak]
up: "[[IKS MOC]]"
status: första pass
---

# Stavfel och språkbruk

## Problematiska kursplaner

<a class="download-xlsx" href="03-IKS/Analys/Stavfel-och-språkbruk.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (8 rader)</span></a>

> [!example]- 8 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [ABQ2B4](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ABQ2B4) | BPO | Dubblerat ord | `en` — …- formulera och muntligt framföra konstruktiv kritik på en en text av vetenskaplig karaktär    - vetenskapligt värdera oc… |
> | [FI1039](https://www.du.se/sv/utbildning/kurser/kursplan/?code=FI1039) | FIA | Dubblerat ord | `have` — …urthermore, on completion of the course, the student should have have the ability to :       - be reflective in relation to probl… |
> | [PE1067](https://www.du.se/sv/utbildning/kurser/kursplan/?code=PE1067) | PEA | Dubblerat ord | `att` — ….m. 2014-01-24.  \## Lärandemål  Kursens övergripande mål är att att den studerande förstår hur man kan styra sina informationsf… |
> | [GPG3AD](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GPG3AD) | PGA | Dubblerat ord | `as` — …ment on the way to the subject teaching profession, as well as as support for being able to make conscious didactic choices d… |
> | [RV1055](https://www.du.se/sv/utbildning/kurser/kursplan/?code=RV1055) | RVA | Dubblerat ord | `samt` — …aminationsformer  En kortare dugga per rättsområde (4x1 hp) samt samt en skriftlig inlämningsuppgift med avslutande seminarie (3,… |
> | [GSO2PL](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSO2PL) | SOA | Dubblerat ord | `credits` — …7.5 credits, Psychological Perspectives on Social Work 7.5 credits credits and Welfare Measures and User Perspective 15 credits… |
> | [GTR2DG](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GTR2DG) | TRU | Dubblerat ord | `the` — …earch. The course is organised into two parts. In part one, the The course introduces students to quantitative research. The co… |
> | [TR3006](https://www.du.se/sv/utbildning/kurser/kursplan/?code=TR3006) | TRU | Dubblerat ord | `the` — …- Independently identify and analyze scientific problems in the the relevant field of knowledge and conduct and report on a pro… |

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
