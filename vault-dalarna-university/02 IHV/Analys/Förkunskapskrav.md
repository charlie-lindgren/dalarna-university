---
tags: [analys, forkunskapskrav]
up: "[[IHV Analys MOC]]"
status: första pass
---

# Förkunskapskrav

## Problematiska kursplaner

<a class="download-xlsx" href="02-IHV/Analys/Förkunskapskrav.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (16 rader)</span></a>

> [!example]- 16 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [AIH237](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AIH237) | IDA | Refererar bekräftat nedlagd kurs | `Idrott` → `IDB009` (nedlagd 2005-08-01); förkunskap nämner nedlagd kurs |
> | [AIH237](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AIH237) | IDA | Refererar bekräftat nedlagd kurs | `Vetenskapsteori` → `GPG263` (nedlagd 2024-03-25); förkunskap nämner nedlagd kurs |
> | [AIH24T](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AIH24T) | IDA | Refererar bekräftat nedlagd kurs | `Idrott` → `IDB009` (nedlagd 2005-08-01); förkunskap nämner nedlagd kurs |
> | [AIH24T](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AIH24T) | IDA | Refererar bekräftat nedlagd kurs | `Vetenskapsteori` → `GPG263` (nedlagd 2024-03-25); förkunskap nämner nedlagd kurs |
> | [GIH37R](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH37R) | IDA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Idrott och hälsa 1 med didaktisk inriktning' |
> | [GIH37R](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH37R) | IDA | Refererar bekräftat nedlagd kurs | `Idrott` → `IDB009` (nedlagd 2005-08-01); förkunskap nämner nedlagd kurs |
> | [GIH37S](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH37S) | IDA | Refererar bekräftat nedlagd kurs | `Idrott` → `IDB009` (nedlagd 2005-08-01); förkunskap nämner nedlagd kurs |
> | [IH2001](https://www.du.se/sv/utbildning/kurser/kursplan/?code=IH2001) | IDA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Idrott 2' |
> | [AMC265](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMC265) | MCA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Diabetesvård I' |
> | [GSA2AF](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA2AF) | SAA | Refererar bekräftat nedlagd kurs | `Organisation` → `FEB021` (nedlagd 2008-03-18); förkunskap nämner nedlagd kurs |
> | [GSA2BV](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA2BV) | SAA | Refererar bekräftat nedlagd kurs | `Organisation` → `FEB021` (nedlagd 2008-03-18); förkunskap nämner nedlagd kurs |
> | [GSA2E4](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA2E4) | SAA | Refererar bekräftat nedlagd kurs | `Organisation` → `FEB021` (nedlagd 2008-03-18); förkunskap nämner nedlagd kurs |
> | [GSA2E5](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA2E5) | SAA | Refererar bekräftat nedlagd kurs | `Organisation` → `FEB021` (nedlagd 2008-03-18); förkunskap nämner nedlagd kurs |
> | [GSA2SD](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA2SD) | SAA | Refererar bekräftat nedlagd kurs | `Organisation` → `FEB021` (nedlagd 2008-03-18); förkunskap nämner nedlagd kurs |
> | [GSA2SE](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA2SE) | SAA | Refererar bekräftat nedlagd kurs | `Organisation` → `FEB021` (nedlagd 2008-03-18); förkunskap nämner nedlagd kurs |
> | [GSA3FK](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA3FK) | SAA | Refererar bekräftat nedlagd kurs | `Organisation` → `FEB021` (nedlagd 2008-03-18); förkunskap nämner nedlagd kurs |

## Syfte

Sektionen *Förkunskapskrav* (på du.se ibland rubricerad *Behörighet* — orden behandlas som synonymer i analysen) beskriver vilka tidigare studier eller motsvarande meriter som krävs för antagning till kursen. Den är central både för antagningsbeslut och för studenter som planerar sin studiegång — saknas eller är ofullständig sektion leder det till otydlighet och ojämn praxis mellan ämnen. Syftet med analysen är att kartlägga **var sektionen saknas helt, var den endast finns på engelska, samt var förkunskapsformuleringen refererar nedlagda kurser** — dels troligt nedlagda (kursnamn saknas i nuvarande katalog) och dels bekräftat nedlagda (kursen finns i QA-cachen av nedlagda kursplaner).

## Metod

Den svenska sektionen läses oavsett om källsidan rubricerar den *Förkunskapskrav* eller *Behörighet* — scrapern (`scripts/scrape_hda_kursplaner.py`) normaliserar bägge rubrikvarianter till `## Förkunskapskrav` i de lokala kursplansfilerna. Den engelska motsvarigheten är `### Prerequisites` (eller alternativa rubriker som *Entry Requirements* / *Admission Requirements*) under `## English Version`. Fyra mönster flaggas:

1. **Sektion saknas** — varken svensk eller engelsk variant finns i kursplanen.
2. **Endast engelsk variant** — `### Prerequisites` har innehåll men `## Förkunskapskrav` saknas eller är tom. Detta är typiskt tecken på en lucka i den svenska källsidan på du.se.
3. **Refererar troligen nedlagd kurs** — bulletten nämner en specifik kurs (mönstret *"kursen X, N hp"* eller bulletten börjar med *"X, N hp"*) men kursnamnet X finns inte bland HDa:s nuvarande kursplaner (aktiva eller vilande). Sannolik indikation på att förkunskapsformuleringen är inaktuell och behöver revideras till nuvarande kursnamn. Endast bullets som nämner ``hp`` granskas — gymnasiekurser som *Engelska 6* eller *Matematik 2b* saknar hp och hoppas över per design.
4. **Refererar bekräftat nedlagd kurs** — namnet matchar en post i QA-cachen `qa/nedlagda-kursplaner/`, dvs. en kursplan som du.se markerat som `status=discontinued`. Detta är ett auktoritativt signal: kursen finns kvar i Dalarnas historiska katalog men erbjuds inte längre, och referensen i förkunskapskravet pekar därför mot en kurs studenten inte kan läsa. Aktivt vault-namn ges företräde om både aktiv och nedlagd version delar namn — den nedlagda flaggas bara om ingen aktiv kurs heter samma sak.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna.
- Svensk sektion `## Förkunskapskrav` (normaliserad från du.se-rubriken *Behörighet* när så förekommer) och engelsk subsektion `### Prerequisites` (motsvarande normalisering på engelska).
- QA-cache av nedlagda kursplaner: `qa/nedlagda-kursplaner/` (skrapas via menyval 7 i `hda.sh`).

## Rekommendationer

1. **Fyll i saknade svenska sektioner** — särskilt prioriterat när engelsk variant redan finns, eftersom innehållet då bara behöver översättas tillbaka.
2. **Uppdatera inaktuella kursreferenser** — när en bullet refererar en kurs som inte längre finns i HDa-katalogen, byt till kursens nuvarande namn eller den ersättande kursen. Kontrollera samtidigt om kraven fortfarande är pedagogiskt relevanta för dagens upplägg. Bekräftat nedlagda referenser (där QA-cachen ger kurskod + nedlagd-datum) prioriteras före troligen-nedlagda — de förra är auktoritativa, de senare bygger på saknad i vaulten.
3. **Lyft frågan i berörda kvalitetsutskott** — bör institutionerna ha gemensamma minimikrav på hur förkunskapskrav formuleras (t.ex. alltid med hp + ämne, eller alltid med exempel på godkänd förkunskap)?
