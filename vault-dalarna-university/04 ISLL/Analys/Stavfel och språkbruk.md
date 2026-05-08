---
tags: [analys, sprak]
up: "[[ISLL MOC]]"
status: första pass
---

# Stavfel och språkbruk

## Problematiska kursplaner

<a class="download-xlsx" href="04-ISLL/Analys/Stavfel-och-språkbruk.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (5 rader)</span></a>

> [!example]- 5 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [AR2001](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AR2001) | ARA | Dubblerat ord | `the` — …resentations of varying length.  ### Assessment  Grades for the the _Grammar and Texts_ module are based on continuous assesmen… |
> | [GFR2A8](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GFR2A8) | FRA | Dubblerat ord | `writing` — …y basic French grammar in their own text production such as writing writing simple texts or summarizing a newspaper article in good Fre… |
> | [GKI3CB](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GKI3CB) | KIA | Dubblerat ord | `and` — …cate unhindered in Chinese on a variety of topics    - read and and understand short authentic Chinese texts    - compose short… |
> | [KI1030](https://www.du.se/sv/utbildning/kurser/kursplan/?code=KI1030) | KIA | Dubblerat ord | `and` — …s such as education, sports, and environment etc.    - read and and comprehend short authentic Chinese texts    - compose short… |
> | [GPR2W2](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GPR2W2) | PRA | Dubblerat ord | `languages` — …cific context and to analyse the dynamics between different languages languages and linguistic varieties from a societal perspective. In th… |

## Syfte

Identifiera **uppenbara skrivfel** (dubblerade ord, kända felstavningar, hunspell-flaggade ord) i kursplaner tvärs Högskolan Dalarnas fyra institutioner. Stavfel skadar inte bara läsningen utan undergräver intrycket av kvalitetsstyrning.

## Metod

Fyra kontroller körs av `qa/check_kursplaner.py`:

1. **Dubblerade ord** — regex `\b(\w{2,})[ \t]+\1\b` med whitelist av legitima upprepningar (*för för, och och, …*).
2. **Kända felstavningar** — två snäva listor (`KNOWN_TYPOS` för svensk text, `KNOWN_TYPOS_EN` för engelsk text) i [`qa/checks_common.py`](../../qa/checks_common.py). Varje fynd visar både den felaktiga formen och föreslagen rättning.
3. **Hunspell sv_SE** — flagga ord som hunspell inte känner igen och som förekommer i färre än fyra filer (sällsynta ord = sannolikare typo, vanliga ord = sannolikare domänterm).
4. **Hunspell en_US** — samma logik mot `## English Version`-sektionen, tröskel < 5 filer.

Båda hunspell-passen filtreras mot omfattande ignorelistor (domäntermer, akronymer, brittiska stavningar). Listorna underhålls i [`qa/checks_common.py`](../../qa/checks_common.py) — när första körningen ger för mycket brus från icke-IIT-vokabulär (vård, språk, samhälle) är det listorna som ska utökas.

**Begränsningar:** Hunspell missar kontextberoende fel (*var/vart*, *de/dem*). Egennamn och facktermer blir falska positiva tills de adderas till ignorelistan.

## Datakälla

- Alla kursplaner under `0X {INST}/Kursplaner/` (IIT + IHV + IKS + ISLL)
- Svensk text: brödtext minus `## English Version`
- Engelsk text: enbart `## English Version`

## Rekommendationer

1. **Korrigera bekräftade stavfel** vid nästa revision av respektive kursplan.
2. **Utöka ignorelistorna i `checks_common.py`** för domäntermer som upprepas i flera kursplaner men inte är felstavningar — särskilt vård- och språkvokabulär som inte finns i UKU-arvet.
3. **Verifiera scrapingartefakter** (sammanskrivna ord som *shouldbe*, *buildingprocess*) genom att jämföra mot källan på du.se. Om de uppstår i scrape-steget bör scrapern normalisera.
4. **Kör båda hunspell-passen efter varje skrape-cykel.**
