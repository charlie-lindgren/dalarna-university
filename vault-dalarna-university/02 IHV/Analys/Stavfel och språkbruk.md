---
tags: [analys, sprak]
up: "[[IHV MOC]]"
status: första pass
---

# Stavfel och språkbruk

## Problematiska kursplaner

<a class="download-xlsx" href="02-IHV/Analys/Stavfel-och-språkbruk.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (6 rader)</span></a>

> [!example]- 6 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [GIH2DB](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH2DB) | IDA | Felstavning | `jämviktsystem` → jämviktssystem |
> | [GIH2DC](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH2DC) | IDA | Felstavning | `jämviktsystem` → jämviktssystem |
> | [GIH33P](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH33P) | IDA | Felstavning | `jämviktsystem` → jämviktssystem |
> | [IH2002](https://www.du.se/sv/utbildning/kurser/kursplan/?code=IH2002) | IDA | Felstavning | `rythm` → rhythm (en) |
> | [GSA2NC](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA2NC) | SAA | Dubblerat ord | `credits` — …7.5 credits, Psychological Perspectives on Social Work 7.5 credits credits and Welfare Measures and User Perspective 15 credits… |
> | [GSA32Y](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA32Y) | SAA | Dubblerat ord | `credits` — …7.5 credits, Psychological Perspectives on Social Work 7.5 credits credits and Welfare Measures and User Perspective 15 credits… |

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
