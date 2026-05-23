---
tags: [analys, forkunskapskrav]
up: "IIT MOC"
status: första pass
---

# Förkunskapskrav

## Problematiska kursplaner

<a class="download-xlsx" href="01-IIT/Analys/Förkunskapskrav.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (5 rader)</span></a>

> [!example]- 5 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [BY1059](https://www.du.se/sv/utbildning/kurser/kursplan/?code=BY1059) | BYA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Byggprojekt småhus' |
> | [GIK2PD](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIK2PD) | IKA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Introduktion till Informatik och eTjänster' |
> | [IK1064](https://www.du.se/sv/utbildning/kurser/kursplan/?code=IK1064) | IKA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Java - Grafiska användargränssnitt med Swing' |
> | [MT1060](https://www.du.se/sv/utbildning/kurser/kursplan/?code=MT1060) | MTA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Mekanik grundläggande kurs' |
> | [EG1012](https://www.du.se/sv/utbildning/kurser/kursplan/?code=EG1012) | MÖY | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Mekanik för energiingenjörer' |

## Syfte

Sektionen *Förkunskapskrav* (på du.se ibland rubricerad *Behörighet* — orden behandlas som synonymer i analysen) beskriver vilka tidigare studier eller motsvarande meriter som krävs för antagning till kursen. Den är central både för antagningsbeslut och för studenter som planerar sin studiegång — saknas eller är ofullständig sektion leder det till otydlighet och ojämn praxis mellan ämnen. Syftet med analysen är att kartlägga **var sektionen saknas helt, var den endast finns på engelska, samt var förkunskapsformuleringen refererar kurser som troligen är nedlagda**.

## Metod

Den svenska sektionen läses oavsett om källsidan rubricerar den *Förkunskapskrav* eller *Behörighet* — scrapern (`scripts/scrape_hda_kursplaner.py`) normaliserar bägge rubrikvarianter till `## Förkunskapskrav` i de lokala kursplansfilerna. Den engelska motsvarigheten är `### Prerequisites` (eller alternativa rubriker som *Entry Requirements* / *Admission Requirements*) under `## English Version`. Tre mönster flaggas:

1. **Sektion saknas** — varken svensk eller engelsk variant finns i kursplanen.
2. **Endast engelsk variant** — `### Prerequisites` har innehåll men `## Förkunskapskrav` saknas eller är tom. Detta är typiskt tecken på en lucka i den svenska källsidan på du.se.
3. **Refererar troligen nedlagd kurs** — bulletten nämner en specifik kurs (mönstret *"kursen X, N hp"* eller bulletten börjar med *"X, N hp"*) men kursnamnet X finns inte bland HDa:s nuvarande kursplaner (aktiva eller vilande). Sannolik indikation på att förkunskapsformuleringen är inaktuell och behöver revideras till nuvarande kursnamn. Endast bullets som nämner ``hp`` granskas — gymnasiekurser som *Engelska 6* eller *Matematik 2b* saknar hp och hoppas över per design.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna.
- Svensk sektion `## Förkunskapskrav` (normaliserad från du.se-rubriken *Behörighet* när så förekommer) och engelsk subsektion `### Prerequisites` (motsvarande normalisering på engelska).

## Rekommendationer

1. **Fyll i saknade svenska sektioner** — särskilt prioriterat när engelsk variant redan finns, eftersom innehållet då bara behöver översättas tillbaka.
2. **Uppdatera inaktuella kursreferenser** — när en bullet refererar en kurs som inte längre finns i HDa-katalogen, byt till kursens nuvarande namn eller den ersättande kursen. Kontrollera samtidigt om kraven fortfarande är pedagogiskt relevanta för dagens upplägg.
3. **Lyft frågan i berörda kvalitetsutskott** — bör institutionerna ha gemensamma minimikrav på hur förkunskapskrav formuleras (t.ex. alltid med hp + ämne, eller alltid med exempel på godkänd förkunskap)?
