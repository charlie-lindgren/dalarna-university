---
tags: [analys, sprak]
up: "[[IIT MOC]]"
status: första pass
---

# Stavfel och språkbruk

## Problematiska kursplaner

<a class="download-xlsx" href="01-IIT/Analys/Stavfel-och-språkbruk.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (16 rader)</span></a>

> [!example]- 16 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [BY2016](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BY2016) | BYA | Felstavning (en) | `knowledges` (en) |
> | [BY2016](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BY2016) | BYA | Felstavning (en) | `xxxxx` (en) |
> | [BFY225](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BFY225) | FYA | Felstavning (en) | `fup` (en) |
> | [BFY226](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BFY226) | FYA | Felstavning (en) | `fup` (en) |
> | [BFY227](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BFY227) | FYA | Felstavning (en) | `fup` (en) |
> | [AIK232](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AIK232) | IKA | Felstavning (en) | `immon` (en) |
> | [GMA2EY](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMA2EY) | MAA | Felstavning | `indicies` → indices (en) |
> | [GMA2EY](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMA2EY) | MAA | Felstavning (en) | `indicies` (en) |
> | [GMT25Z](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMT25Z) | MTA | Felstavning | `startgodkännandeformulär` (sv) |
> | [AEG225](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AEG225) | MÖY | Felstavning | `produktionskattelättnader` (sv) |
> | [GEG2ZQ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GEG2ZQ) | MÖY | Felstavning | `solcellsanläggingar` → solcellsanläggningar |
> | [GEG2ZQ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GEG2ZQ) | MÖY | Felstavning | `solcellsanläggingar` (sv) |
> | [GSQ25K](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ25K) | SQQ | Felstavning | `skalnivåer` (sv) |
> | [GSQ33N](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ33N) | SQQ | Felstavning | `skalnivåer` (sv) |
> | [GMI23G](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMI23G) | XYZ | Felstavning (en) | `euclidian` (en) |
> | [GMI2C8](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMI2C8) | XYZ | Felstavning (en) | `mathodology` (en) |

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
