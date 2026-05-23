---
tags: [analys, forkunskapskrav]
up: "[[ISLL MOC]]"
status: första pass
---

# Förkunskapskrav

## Problematiska kursplaner

<a class="download-xlsx" href="04-ISLL/Analys/Förkunskapskrav.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (10 rader)</span></a>

> [!example]- 10 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [EN3077](https://www.du.se/sv/utbildning/kurser/kursplan/?code=EN3077) | ENA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Engelska: Språkvetenskap i tal och skrift' |
> | [GSP2YT](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSP2YT) | SPA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Spanska I: Skriftlig språkfärdighet och grammatik' |
> | [SP1050](https://www.du.se/sv/utbildning/kurser/kursplan/?code=SP1050) | SPA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Spanska I: Skriftlig språkfärdighet och grammatik' |
> | [SP1051](https://www.du.se/sv/utbildning/kurser/kursplan/?code=SP1051) | SPA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Spanska I: Skriftlig språkfärdighet och grammatik' |
> | [SP1052](https://www.du.se/sv/utbildning/kurser/kursplan/?code=SP1052) | SPA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Spanska I: Skriftlig språkfärdighet och grammatik' |
> | [SP1053](https://www.du.se/sv/utbildning/kurser/kursplan/?code=SP1053) | SPA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Spanska I: Skriftlig språkfärdighet och grammatik' |
> | [TY1069](https://www.du.se/sv/utbildning/kurser/kursplan/?code=TY1069) | TYA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Tysk grammatik och textkommentar' |
> | [TY2004](https://www.du.se/sv/utbildning/kurser/kursplan/?code=TY2004) | TYA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Muntlig språkfärdighet med kulturkunskap II' |
> | [TY2007](https://www.du.se/sv/utbildning/kurser/kursplan/?code=TY2007) | TYA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Muntlig språkfärdighet med kulturkunskap II' |
> | [TY2008](https://www.du.se/sv/utbildning/kurser/kursplan/?code=TY2008) | TYA | Refererar troligen nedlagd kurs | Refererad kurs hittas ej i vaulten (troligen nedlagd): 'Språk- och kulturhistoria med uppsats' |

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
