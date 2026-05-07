---
tags: [analys, sprak]
up: "[[IIT MOC]]"
status: första pass
---

# Stavfel och språkbruk

## Problematiska kursplaner

<a class="download-xlsx" href="Stavfel-och-språkbruk.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (27 rader)</span></a>

> [!example]- 27 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [ABY2BL](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ABY2BL) | BYA | Felstavning (en) | `witten` (en) |
> | [BY1047](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BY1047) | BYA | Felstavning (en) | `buildingprocess` (en) |
> | [BY1047](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BY1047) | BYA | Felstavning (en) | `competion` (en) |
> | [BY1047](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BY1047) | BYA | Felstavning (en) | `shouldbe` (en) |
> | [BFY224](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BFY224) | FYA | Felstavning | `preparandnivå` (sv) |
> | [BFY225](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BFY225) | FYA | Felstavning (en) | `fup` (en) |
> | [BFY226](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BFY226) | FYA | Felstavning (en) | `fup` (en) |
> | [BFY227](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BFY227) | FYA | Felstavning (en) | `fup` (en) |
> | [AIK232](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AIK232) | IKA | Felstavning (en) | `immon` (en) |
> | [GIK29B](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIK29B) | IKA | Felstavning (en) | `vgs` (en) |
> | [GMA2EY](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMA2EY) | MAA | Felstavning (en) | `indicies` (en) |
> | [MA0011](https://www.du.se/sv/utbildning/kurser/kursplan/?code=MA0011) | MAA | Felstavning | `preparandnivå` (sv) |
> | [MA0013](https://www.du.se/sv/utbildning/kurser/kursplan/?code=MA0013) | MAA | Felstavning | `preparandnivå` (sv) |
> | [GMD2PA](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMD2PA) | MDI | Felstavning (en) | `exeptions` (en) |
> | [GMT34K](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMT34K) | MTA | Felstavning (en) | `programing` (en) |
> | [GMT34R](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMT34R) | MTA | Felstavning (en) | `variousengineering` (en) |
> | [AEG2AL](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AEG2AL) | MÖY | Felstavning (en) | `andrelate` (en) |
> | [AEG2AQ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AEG2AQ) | MÖY | Felstavning (en) | `adress` (en) |
> | [AEG2C5](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AEG2C5) | MÖY | Felstavning (en) | `laboatory` (en) |
> | [EG3014](https://www.du.se/sv/utbildning/kurser/kursplan/?code=EG3014) | MÖY | Felstavning (en) | `appropiate` (en) |
> | [EG3014](https://www.du.se/sv/utbildning/kurser/kursplan/?code=EG3014) | MÖY | Felstavning (en) | `crediits` (en) |
> | [GEG2ZR](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GEG2ZR) | MÖY | Felstavning | `inlämingsuppgifter` (sv) |
> | [GSQ33N](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSQ33N) | SQQ | Felstavning | `skalniåver` (sv) |
> | [GMI23G](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMI23G) | XYZ | Felstavning (en) | `eulides` (en) |
> | [GMI2C8](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMI2C8) | XYZ | Felstavning (en) | `credtis` (en) |
> | [GMI2C8](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMI2C8) | XYZ | Felstavning (en) | `mathodology` (en) |
> | [GMI2J3](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMI2J3) | XYZ | Felstavning (en) | `discusess` (en) |

## Syfte

Identifiera **uppenbara skrivfel** (dubblerade ord, kända felstavningar, hunspell-flaggade ord) i kursplaner tvärs Högskolan Dalarnas fyra institutioner. Stavfel skadar inte bara läsningen utan undergräver intrycket av kvalitetsstyrning.

## Metod

Fyra kontroller körs av `qa/check_kursplaner.py`:

1. **Dubblerade ord** — regex `\b(\w{2,})[ \t]+\1\b` med whitelist av legitima upprepningar (*för för, och och, …*).
2. **Kända felstavningar** — snäv lista med återkommande typos (*adminstrat*, *infomation*, *såväll*, *tilsammans*).
3. **Hunspell sv_SE** — flagga ord som hunspell inte känner igen och som förekommer i färre än fyra filer (sällsynta ord = sannolikare typo, vanliga ord = sannolikare domänterm).
4. **Hunspell en_US** — samma logik mot `## English Version`-sektionen, tröskel < 5 filer.

Båda hunspell-passen filtreras mot omfattande ignorelistor (domäntermer, akronymer, brittiska stavningar). Listorna underhålls i [`qa/checks_common.py`](../../qa/checks_common.py) — när första körningen ger för mycket brus från icke-IIT-vokabulär (vård, språk, samhälle) är det listorna som ska utökas.

**Begränsningar:** Hunspell missar kontextberoende fel (*var/vart*, *de/dem*). Egennamn och facktermer blir falska positiva tills de adderas till ignorelistan.

## Datakälla

- Alla kursplaner under `0X {INST}/Kursplaner/` (IIT + IHV + IKS + ISLL)
- Svensk text: brödtext minus `## English Version`
- Engelsk text: enbart `## English Version`

## Resultat

*Fylls i efter första genomgång — se tabellen ovan för rådata från senaste QA-körningen.*

## Observationer

*Fylls i efter första genomgång.*

## Rekommendationer

1. **Korrigera bekräftade stavfel** vid nästa revision av respektive kursplan.
2. **Utöka ignorelistorna i `checks_common.py`** för domäntermer som upprepas i flera kursplaner men inte är felstavningar — särskilt vård- och språkvokabulär som inte finns i UKU-arvet.
3. **Verifiera scrapingartefakter** (sammanskrivna ord som *shouldbe*, *buildingprocess*) genom att jämföra mot källan på du.se. Om de uppstår i scrape-steget bör scrapern normalisera.
4. **Kör båda hunspell-passen efter varje skrape-cykel.**
