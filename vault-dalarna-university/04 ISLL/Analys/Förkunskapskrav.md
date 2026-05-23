---
tags: [analys, forkunskapskrav]
up: "[[ISLL MOC]]"
status: första pass
---

# Förkunskapskrav

## Problematiska kursplaner

<a class="download-xlsx" href="04-ISLL/Analys/Förkunskapskrav.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (19 rader)</span></a>

> [!example]- 19 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [GAR38K](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GAR38K) | ARA | Osannolikt kort innehåll | Osannolikt kort (19 tecken): '- Arabiska I, 15 hp' |
> | [GAR38L](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GAR38L) | ARA | Osannolikt kort innehåll | Osannolikt kort (20 tecken): '- Arabiska II, 15 hp' |
> | [GAR38M](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GAR38M) | ARA | Osannolikt kort innehåll | Osannolikt kort (21 tecken): '- Arabiska III, 15 hp' |
> | [GAR38N](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GAR38N) | ARA | Osannolikt kort innehåll | Osannolikt kort (20 tecken): '- Arabiska IV, 15 hp' |
> | [GAR39K](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GAR39K) | ARA | Osannolikt kort innehåll | Osannolikt kort (20 tecken): '- Arabiska II, 15 hp' |
> | [GAR39L](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GAR39L) | ARA | Osannolikt kort innehåll | Osannolikt kort (19 tecken): '- Arabiska V, 15 hp' |
> | [GAR39M](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GAR39M) | ARA | Osannolikt kort innehåll | Osannolikt kort (19 tecken): '- Arabiska V, 15 hp' |
> | [GEN222](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GEN222) | ENA | Osannolikt kort innehåll | Osannolikt kort (13 tecken): '- Lärarexamen' |
> | [GEN3DG](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GEN3DG) | ENA | Osannolikt kort innehåll | Osannolikt kort (21 tecken): '- Engelska I, 22,5 hp' |
> | [GEN3K3](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GEN3K3) | ENA | Osannolikt kort innehåll | Osannolikt kort (21 tecken): '- Engelska I, 22,5 hp' |
> | [AKI28Z](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AKI28Z) | KIA | Osannolikt kort innehåll | Osannolikt kort (24 tecken): '- Examen om minst 180 hp' |
> | [AKI292](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AKI292) | KIA | Osannolikt kort innehåll | Osannolikt kort (24 tecken): '- Examen om minst 180 hp' |
> | [GSP2JH](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSP2JH) | SPA | Osannolikt kort innehåll | Osannolikt kort (13 tecken): '- Lärarexamen' |
> | [GSS2G8](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSS2G8) | SSA | Osannolikt kort innehåll | Osannolikt kort (13 tecken): '- Lärarexamen' |
> | [GSS2JA](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSS2JA) | SSA | Osannolikt kort innehåll | Osannolikt kort (13 tecken): '- Lärarexamen' |
> | [GSS2XE](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSS2XE) | SSA | Osannolikt kort innehåll | Osannolikt kort (13 tecken): '- Lärarexamen' |
> | [SS1085](https://www.du.se/sv/utbildning/kurser/kursplan/?code=SS1085) | SSA | Osannolikt kort innehåll | Osannolikt kort (13 tecken): '- Lärarexamen' |
> | [ASV2CP](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ASV2CP) | SVE | Osannolikt kort innehåll | Osannolikt kort (19 tecken): '- Lärarlegitimation' |
> | [ASV2CQ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ASV2CQ) | SVE | Osannolikt kort innehåll | Osannolikt kort (19 tecken): '- Lärarlegitimation' |

## Syfte

Sektionen *Förkunskapskrav* (på du.se ibland rubricerad *Behörighet* — orden behandlas som synonymer i analysen) beskriver vilka tidigare studier eller motsvarande meriter som krävs för antagning till kursen. Den är central både för antagningsbeslut och för studenter som planerar sin studiegång — saknas eller är ofullständig sektion leder det till otydlighet och ojämn praxis mellan ämnen. Syftet med analysen är att kartlägga **var sektionen saknas helt, var den endast finns på engelska, var innehållet är osannolikt kort, samt var svensk och engelsk version skiljer sig markant i längd**.

## Metod

Den svenska sektionen läses oavsett om källsidan rubricerar den *Förkunskapskrav* eller *Behörighet* — scrapern (`scripts/scrape_hda_kursplaner.py`) normaliserar bägge rubrikvarianter till `## Förkunskapskrav` i de lokala kursplansfilerna. Den engelska motsvarigheten är `### Prerequisites` (eller alternativa rubriker som *Entry Requirements* / *Admission Requirements*) under `## English Version`. Fyra mönster flaggas:

1. **Sektion saknas** — varken svensk eller engelsk variant finns i kursplanen.
2. **Endast engelsk variant** — `### Prerequisites` har innehåll men `## Förkunskapskrav` saknas eller är tom. Detta är typiskt tecken på en lucka i den svenska källsidan på du.se.
3. **Osannolikt kort innehåll** — den svenska texten är kortare än 25 tecken (t.ex. *"- Lärarexamen"*, *"- 60 hp"*) och saknar därmed sannolikt ämnes- eller områdesspecifikation.
4. **Stor sv/en-längdskillnad** — den ena versionen är minst två gånger så lång som den andra (båda måste vara över 30 tecken för att räknas). Detta fångar fall där förkunskapskraven har förlängts på den ena språksidan utan motsvarande uppdatering på den andra.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna.
- Svensk sektion `## Förkunskapskrav` (normaliserad från du.se-rubriken *Behörighet* när så förekommer) och engelsk subsektion `### Prerequisites` (motsvarande normalisering på engelska).

## Rekommendationer

1. **Fyll i saknade svenska sektioner** — särskilt prioriterat när engelsk variant redan finns, eftersom innehållet då bara behöver översättas tillbaka.
2. **Komplettera tunna formuleringar** — *"- Lärarexamen"* eller *"- 60 hp"* räcker sällan; ange ämne eller huvudområde (t.ex. *"- Lärarexamen med inriktning mot grundskolan"*, *"- 60 hp i huvudområdet X"*).
3. **Synka sv/en-paritet** — när en av versionerna uppdateras bör den andra följa med samma omgång, annars uppstår skillnader som senare blir svåra att spåra till en specifik revidering.
4. **Lyft frågan i berörda kvalitetsutskott** — bör institutionerna ha gemensamma minimikrav på hur förkunskapskrav formuleras (t.ex. alltid med hp + ämne, eller alltid med exempel på godkänd förkunskap)?
