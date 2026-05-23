---
tags: [analys, forkunskapskrav]
up: "[[IHV MOC]]"
status: första pass
---

# Förkunskapskrav

## Problematiska kursplaner

<a class="download-xlsx" href="02-IHV/Analys/Förkunskapskrav.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (9 rader)</span></a>

> [!example]- 9 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [GIH37R](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH37R) | IDA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Idrott och hälsa 1 med didaktisk inriktning' |
> | [IH2001](https://www.du.se/sv/utbildning/kurser/kursplan/?code=IH2001) | IDA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Idrott 2' |
> | [AMC265](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMC265) | MCA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Diabetesvård I' |
> | [AMC28N](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMC28N) | MCA | Endast engelsk variant | Engelska Prerequisites finns (87 tecken) men svenska saknas |
> | [AMC29F](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMC29F) | MCA | Endast engelsk variant | Engelska Prerequisites finns (142 tecken) men svenska saknas |
> | [AMC2BG](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AMC2BG) | MCA | Stor sv/en-längdskillnad | Längdskillnad sv 39 tecken vs en 84 tecken (×2.2) |
> | [VV3003](https://www.du.se/sv/utbildning/kurser/kursplan/?code=VV3003) | VÅE | Stor sv/en-längdskillnad | Längdskillnad sv 183 tecken vs en 35 tecken (×5.2) |
> | [VV3004](https://www.du.se/sv/utbildning/kurser/kursplan/?code=VV3004) | VÅE | Stor sv/en-längdskillnad | Längdskillnad sv 104 tecken vs en 35 tecken (×3.0) |
> | [VV3009](https://www.du.se/sv/utbildning/kurser/kursplan/?code=VV3009) | VÅE | Stor sv/en-längdskillnad | Längdskillnad sv 467 tecken vs en 219 tecken (×2.1) |

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
