---
tags: [analys, forkunskapskrav]
up: "[[IKS MOC]]"
status: första pass
---

# Förkunskapskrav

## Problematiska kursplaner

<a class="download-xlsx" href="03-IKS/Analys/Förkunskapskrav.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (13 rader)</span></a>

> [!example]- 13 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [AU3005](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AU3005) | BPO | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Audiovisuella studier: Kunskapsproduktion och gestaltning' |
> | [GBQ29E](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GBQ29E) | BPO | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Bildproduktion: Teori och Metod' |
> | [GBQ2AZ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GBQ2AZ) | BPO | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Det cinematiska språket: Mise-en-scène' |
> | [KG1016](https://www.du.se/sv/utbildning/kurser/kursplan/?code=KG1016) | KGA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Demography and Markets for Tourism' |
> | [KG3010](https://www.du.se/sv/utbildning/kurser/kursplan/?code=KG3010) | KGA | Stor sv/en-längdskillnad | Längdskillnad sv 32 tecken vs en 79 tecken (×2.5) |
> | [GLP29S](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GLP29S) | LPU | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Radioproduktion' |
> | [GLP2KH](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GLP2KH) | LPU | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Radioproduktion' |
> | [APG2AJ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG2AJ) | PGA | Stor sv/en-längdskillnad | Längdskillnad sv 65 tecken vs en 132 tecken (×2.0) |
> | [APG2BK](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG2BK) | PGA | Stor sv/en-längdskillnad | Längdskillnad sv 47 tecken vs en 99 tecken (×2.1) |
> | [GPG3FT](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GPG3FT) | PGA | Stor sv/en-längdskillnad | Längdskillnad sv 48 tecken vs en 122 tecken (×2.5) |
> | [PG2043](https://www.du.se/sv/utbildning/kurser/kursplan/?code=PG2043) | PGA | Stor sv/en-längdskillnad | Längdskillnad sv 240 tecken vs en 31 tecken (×7.7) |
> | [RK3043](https://www.du.se/sv/utbildning/kurser/kursplan/?code=RK3043) | RKA | Stor sv/en-längdskillnad | Längdskillnad sv 108 tecken vs en 54 tecken (×2.0) |
> | [RV1055](https://www.du.se/sv/utbildning/kurser/kursplan/?code=RV1055) | RVA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Perspektiv på företagande' |

## Syfte

Sektionen *Förkunskapskrav* (på du.se ibland rubricerad *Behörighet* — orden behandlas som synonymer i analysen) beskriver vilka tidigare studier eller motsvarande meriter som krävs för antagning till kursen. Den är central både för antagningsbeslut och för studenter som planerar sin studiegång — saknas eller är ofullständig sektion leder det till otydlighet och ojämn praxis mellan ämnen. Syftet med analysen är att kartlägga **var sektionen saknas helt, var den endast finns på engelska, var svensk och engelsk version skiljer sig markant i längd, samt var förkunskapsformuleringen refererar kurser som troligen är nedlagda**.

## Metod

Den svenska sektionen läses oavsett om källsidan rubricerar den *Förkunskapskrav* eller *Behörighet* — scrapern (`scripts/scrape_hda_kursplaner.py`) normaliserar bägge rubrikvarianter till `## Förkunskapskrav` i de lokala kursplansfilerna. Den engelska motsvarigheten är `### Prerequisites` (eller alternativa rubriker som *Entry Requirements* / *Admission Requirements*) under `## English Version`. Fyra mönster flaggas:

1. **Sektion saknas** — varken svensk eller engelsk variant finns i kursplanen.
2. **Endast engelsk variant** — `### Prerequisites` har innehåll men `## Förkunskapskrav` saknas eller är tom. Detta är typiskt tecken på en lucka i den svenska källsidan på du.se.
3. **Stor sv/en-längdskillnad** — den ena versionen är minst två gånger så lång som den andra (båda måste vara över 30 tecken för att räknas). Detta fångar fall där förkunskapskraven har förlängts på den ena språksidan utan motsvarande uppdatering på den andra.
4. **Refererar troligen nedlagd kurs** — bulletten nämner en specifik kurs (mönstret *"kursen X, N hp"* eller bulletten börjar med *"X, N hp"*) men kursnamnet X finns inte bland HDa:s nuvarande kursplaner (aktiva eller vilande). Sannolik indikation på att förkunskapsformuleringen är inaktuell och behöver revideras till nuvarande kursnamn. Endast bullets som nämner ``hp`` granskas — gymnasiekurser som *Engelska 6* eller *Matematik 2b* saknar hp och hoppas över per design.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna.
- Svensk sektion `## Förkunskapskrav` (normaliserad från du.se-rubriken *Behörighet* när så förekommer) och engelsk subsektion `### Prerequisites` (motsvarande normalisering på engelska).

## Rekommendationer

1. **Fyll i saknade svenska sektioner** — särskilt prioriterat när engelsk variant redan finns, eftersom innehållet då bara behöver översättas tillbaka.
2. **Synka sv/en-paritet** — när en av versionerna uppdateras bör den andra följa med samma omgång, annars uppstår skillnader som senare blir svåra att spåra till en specifik revidering.
3. **Uppdatera inaktuella kursreferenser** — när en bullet refererar en kurs som inte längre finns i HDa-katalogen, byt till kursens nuvarande namn eller den ersättande kursen. Kontrollera samtidigt om kraven fortfarande är pedagogiskt relevanta för dagens upplägg.
4. **Lyft frågan i berörda kvalitetsutskott** — bör institutionerna ha gemensamma minimikrav på hur förkunskapskrav formuleras (t.ex. alltid med hp + ämne, eller alltid med exempel på godkänd förkunskap)?
