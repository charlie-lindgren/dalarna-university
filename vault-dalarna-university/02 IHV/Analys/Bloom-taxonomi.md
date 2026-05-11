---
tags: [analys, bloom, larandemal]
up: "[[IHV MOC]]"
status: första pass
---

# Bloom-taxonomi

## Problematiska kursplaner

<a class="download-xlsx" href="02-IHV/Analys/Bloom-taxonomi.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (20 rader)</span></a>

> [!example]- 20 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [GIH2D6](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH2D6) | IDA | Okänt ledande verb | 3 av 4 bullets har okänt ledande verb |
> | [GIH2D7](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH2D7) | IDA | Okänt ledande verb | 3 av 4 bullets har okänt ledande verb |
> | [GIH2G4](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH2G4) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,1,0,1,1] |
> | [GIH2VK](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH2VK) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,0,0,0,0,2] |
> | [GIH37B](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH37B) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,0,0,1,1,2] |
> | [GIH37C](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH37C) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,0,1,1,2] |
> | [GIH39B](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH39B) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,0,0,1,1,2] |
> | [GIH39C](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH39C) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,0,1,1,2] |
> | [GIH3AQ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH3AQ) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,0,1,0,4,0] |
> | [GIH3G4](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH3G4) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,0,0,1,1] |
> | [GIH3G7](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GIH3G7) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,0,0,0,2,2] |
> | [IH1006](https://www.du.se/sv/utbildning/kurser/kursplan/?code=IH1006) | IDA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,0,0,0,1,1] |
> | [IH3007](https://www.du.se/sv/utbildning/kurser/kursplan/?code=IH3007) | IDA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,1,3,0,0,0] |
> | [GSA27Y](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSA27Y) | SAA | Okänt ledande verb | 5 av 9 bullets har okänt ledande verb |
> | [ASR22N](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ASR22N) | SRP | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [4,1,1,0,0,0] |
> | [SR3015](https://www.du.se/sv/utbildning/kurser/kursplan/?code=SR3015) | SRP | Okänt ledande verb | 3 av 14 bullets har okänt ledande verb |
> | [VV3007](https://www.du.se/sv/utbildning/kurser/kursplan/?code=VV3007) | VÅE | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [5,0,2,0,0,0] |
> | [VV3010](https://www.du.se/sv/utbildning/kurser/kursplan/?code=VV3010) | VÅE | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [4,0,2,0,0,0] |
> | [VV3011](https://www.du.se/sv/utbildning/kurser/kursplan/?code=VV3011) | VÅE | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,0,4,0,0,0] |
> | [VV3011](https://www.du.se/sv/utbildning/kurser/kursplan/?code=VV3011) | VÅE | Okänt ledande verb | 14 av 19 bullets har okänt ledande verb |

## Syfte


Lärandemålens **verbnivå bör matcha kursnivån**. En kurs på *avancerad nivå* vars lärandemål bara rör sig på Minnas/Förstå-nivå indikerar att kursen ligger lägre kognitivt än nivåklassningen anger; en kurs på *grundnivå* där värdera/skapa-verb dominerar kan tyda på fellabeling eller på en kurs som egentligen tillhör avancerad nivå. Det är ett pedagogiskt och formellt problem (Bologna, examensordningen).

## Metod

För varje punkt i sektionen `Lärandemål` (svensk version) klassificeras det **första klassbara verbet** mot ett svenskt verb-lexikon strukturerat enligt de sex reviderade Bloom-nivåerna (1 Minnas → 2 Förstå → 3 Tillämpa → 4 Analysera → 5 Värdera → 6 Skapa). Ledande adverb (*självständigt*, *muntligt*) hoppas över. Kursnivån läses från kursplanens metadata (*Grundnivå* eller *Avancerad nivå*) — inte från kurskodprefix, eftersom prefix som G2 faktiskt kan beteckna grundnivå.

Tre regler ger fynd:

- **Låg verbnivå för avancerad kurs** — kursen är på avancerad nivå men inga lärandemål ligger på nivå 4–6 (Analysera/Värdera/Skapa).
- **Hög verbnivå för grundkurs** — kursen är på grundnivå men ≥ 60 % av klassade lärandemål ligger på nivå 5–6 (Värdera/Skapa).
- **Okänt verb** — ≥ 3 lärandemål inleds med ett verb som inte finns i lexikonet. Inte ett kvalitetsfel i sig, utan en signal att utöka lexikonet.

Detalj-strängen för varje fynd visar fördelningen som ett 6-cells histogram, t.ex. *fördelning [2,3,1,0,0,0]* (cell 1 = Minnas, cell 6 = Skapa).

**Begränsningar:**

- Lexikonet är handkurerat och ofullständigt — utökas iterativt utifrån fynd av okända verb.
- Kontext räknas inte: *"redogöra för komplexa samband"* kan vara ett kvalificerat lärandemål trots Minnas-verbet.
- Vid dubbelplacerade verb (t.ex. *jämföra* mellan Förstå och Analysera) väljs alltid den högsta nivån.
- Endast svenska analyseras; engelska Learning Outcomes granskas inte här.

Listan ska användas som diskussionsunderlag — granskaren bedömer varje fynd i sitt sammanhang.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna (IIT, IHV, IKS, ISLL).
- Endast svensk version, sektionen `Lärandemål`.
- Kursnivå läses från kursplanens metadata (*Grundnivå* / *Avancerad nivå*).

## Rekommendationer

1. **Granska varje flaggad kursplan manuellt** med kontext från syftesbeskrivning, examination och kurslitteratur.
2. **Komplettera lärandemålen med höga Bloom-verb** vid nästa revision om kontext bekräftar att kursen faktiskt ligger på avancerad nivå.
3. **Överväg nivåflyttning** om ett konsekvent mönster av låga verb finns — kursen kanske borde vara grundnivå.
