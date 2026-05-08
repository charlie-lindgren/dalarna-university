---
tags: [analys, bloom, larandemal]
up: "[[IKS MOC]]"
status: första pass
---

# Bloom-taxonomi

## Problematiska kursplaner

<a class="download-xlsx" href="03-IKS/Analys/Bloom-taxonomi.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (67 rader)</span></a>

> [!example]- 67 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [AB1005](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AB1005) | ABA | Okänt ledande verb | 3 av 5 bullets har okänt ledande verb |
> | [AB1006](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AB1006) | ABA | Okänt ledande verb | 9 av 10 bullets har okänt ledande verb |
> | [AB1009](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AB1009) | ABA | Okänt ledande verb | 5 av 5 bullets har okänt ledande verb |
> | [AB1014](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AB1014) | ABA | Okänt ledande verb | 4 av 12 bullets har okänt ledande verb |
> | [AB1029](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AB1029) | ABA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,1,0,0,3,0] |
> | [AB3001](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AB3001) | ABA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [3,1,0,0,0,0] |
> | [ABQ2B2](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ABQ2B2) | BPO | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,1,1,0,0,0] |
> | [GBQ2NP](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GBQ2NP) | BPO | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,1,0,1,1] |
> | [GBQ2QB](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GBQ2QB) | BPO | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,0,2,3,2] |
> | [GBQ2U9](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GBQ2U9) | BPO | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,1,0,1,1] |
> | [GBQ36D](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GBQ36D) | BPO | Okänt ledande verb | 3 av 9 bullets har okänt ledande verb |
> | [FI1028](https://www.du.se/sv/utbildning/kurser/kursplan/?code=FI1028) | FIA | Okänt ledande verb | 5 av 10 bullets har okänt ledande verb |
> | [FI1031](https://www.du.se/sv/utbildning/kurser/kursplan/?code=FI1031) | FIA | Okänt ledande verb | 4 av 9 bullets har okänt ledande verb |
> | [FI1033](https://www.du.se/sv/utbildning/kurser/kursplan/?code=FI1033) | FIA | Okänt ledande verb | 4 av 9 bullets har okänt ledande verb |
> | [FI1038](https://www.du.se/sv/utbildning/kurser/kursplan/?code=FI1038) | FIA | Okänt ledande verb | 4 av 10 bullets har okänt ledande verb |
> | [FI1039](https://www.du.se/sv/utbildning/kurser/kursplan/?code=FI1039) | FIA | Okänt ledande verb | 3 av 7 bullets har okänt ledande verb |
> | [GFI293](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GFI293) | FIA | Okänt ledande verb | 4 av 10 bullets har okänt ledande verb |
> | [AHI263](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AHI263) | HIA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,3,0,0,0,0] |
> | [AHI26P](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AHI26P) | HIA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,3,0,0,0,0] |
> | [AHI29Q](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AHI29Q) | HIA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,2,0,0,0,0] |
> | [AS3016](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3016) | HIA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [4,0,0,0,0,0] |
> | [AS3020](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3020) | HIA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [4,0,0,0,0,0] |
> | [AS3022](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3022) | HIA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [3,0,0,0,0,0] |
> | [AS3023](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3023) | HIA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,1,0,0,0,0] |
> | [AS3024](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3024) | HIA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [3,0,0,0,0,0] |
> | [KG2001](https://www.du.se/sv/utbildning/kurser/kursplan/?code=KG2001) | KGA | Okänt ledande verb | 7 av 16 bullets har okänt ledande verb |
> | [KG3011](https://www.du.se/sv/utbildning/kurser/kursplan/?code=KG3011) | KGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [3,0,3,0,0,0] |
> | [GLP234](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GLP234) | LPU | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,0,0,1,2] |
> | [GLP2MU](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GLP2MU) | LPU | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,1,0,0,0,2] |
> | [GLP2QX](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GLP2QX) | LPU | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,1,0,0,0,2] |
> | [LP1071](https://www.du.se/sv/utbildning/kurser/kursplan/?code=LP1071) | LPU | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [0,0,0,0,1,2] |
> | [GMN3EZ](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GMN3EZ) | MPR | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,0,0,1,0,3] |
> | [NA1003](https://www.du.se/sv/utbildning/kurser/kursplan/?code=NA1003) | NAA | Okänt ledande verb | 5 av 10 bullets har okänt ledande verb |
> | [NA1026](https://www.du.se/sv/utbildning/kurser/kursplan/?code=NA1026) | NAA | Okänt ledande verb | 6 av 10 bullets har okänt ledande verb |
> | [NA1027](https://www.du.se/sv/utbildning/kurser/kursplan/?code=NA1027) | NAA | Okänt ledande verb | 4 av 10 bullets har okänt ledande verb |
> | [NA3001](https://www.du.se/sv/utbildning/kurser/kursplan/?code=NA3001) | NAA | Okänt ledande verb | 4 av 10 bullets har okänt ledande verb |
> | [NA3007](https://www.du.se/sv/utbildning/kurser/kursplan/?code=NA3007) | NAA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [0,7,1,0,0,0] |
> | [NA3008](https://www.du.se/sv/utbildning/kurser/kursplan/?code=NA3008) | NAA | Okänt ledande verb | 4 av 4 bullets har okänt ledande verb |
> | [PE1069](https://www.du.se/sv/utbildning/kurser/kursplan/?code=PE1069) | PEA | Hög verbnivå för grundkurs | Grundkurs domineras av värdera/skapa; fördelning [1,0,0,0,0,2] |
> | [APG24E](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG24E) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [7,0,0,0,0,0] |
> | [APG24S](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG24S) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [3,0,0,0,0,0] |
> | [APG27T](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG27T) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [5,0,0,0,0,0] |
> | [APG27U](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG27U) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [7,0,0,0,0,0] |
> | [APG27Z](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG27Z) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [12,0,0,0,0,0] |
> | [APG282](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG282) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [8,0,0,0,0,0] |
> | [APG28B](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG28B) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [10,0,0,0,0,0] |
> | [APG28M](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG28M) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [5,0,0,0,0,0] |
> | [APG28R](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG28R) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [9,0,0,0,0,0] |
> | [APG28S](https://www.du.se/sv/utbildning/kurser/kursplan/?code=APG28S) | PGA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [9,0,0,0,0,0] |
> | [GPG3EV](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GPG3EV) | PGA | Okänt ledande verb | 3 av 13 bullets har okänt ledande verb |
> | [PG3069](https://www.du.se/sv/utbildning/kurser/kursplan/?code=PG3069) | PGA | Okänt ledande verb | 3 av 5 bullets har okänt ledande verb |
> | [ARK29H](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ARK29H) | RKA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [0,3,0,0,0,0] |
> | [GRK2Q5](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GRK2Q5) | RKA | Okänt ledande verb | 3 av 11 bullets har okänt ledande verb |
> | [RV1009](https://www.du.se/sv/utbildning/kurser/kursplan/?code=RV1009) | RVA | Okänt ledande verb | 3 av 5 bullets har okänt ledande verb |
> | [RV1015](https://www.du.se/sv/utbildning/kurser/kursplan/?code=RV1015) | RVA | Okänt ledande verb | 3 av 6 bullets har okänt ledande verb |
> | [RV1037](https://www.du.se/sv/utbildning/kurser/kursplan/?code=RV1037) | RVA | Okänt ledande verb | 3 av 6 bullets har okänt ledande verb |
> | [RV1043](https://www.du.se/sv/utbildning/kurser/kursplan/?code=RV1043) | RVA | Okänt ledande verb | 4 av 11 bullets har okänt ledande verb |
> | [ASK22L](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ASK22L) | SKA | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [6,0,2,0,0,0] |
> | [GSO2PL](https://www.du.se/sv/utbildning/kurser/kursplan/?code=GSO2PL) | SOA | Okänt ledande verb | 3 av 10 bullets har okänt ledande verb |
> | [ATR26B](https://www.du.se/sv/utbildning/kurser/kursplan/?code=ATR26B) | TRU | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [4,1,1,0,0,0] |
> | [AS3002](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3002) | UVX | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [3,0,0,0,0,0] |
> | [AS3003](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3003) | UVX | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,1,0,0,0,0] |
> | [AS3004](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3004) | UVX | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [3,0,0,0,0,0] |
> | [AS3008](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3008) | UVX | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [4,0,0,0,0,0] |
> | [AS3012](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS3012) | UVX | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [4,0,0,0,0,0] |
> | [AS4001](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS4001) | UVX | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [1,0,1,0,0,0] |
> | [AS4003](https://www.du.se/sv/utbildning/kurser/kursplan/?code=AS4003) | UVX | Låg verbnivå för avancerad kurs | Avancerad kurs utan analysera/värdera/skapa-verb; fördelning [3,0,0,0,0,0] |

## Syfte


Lärandemålens **verbnivå bör matcha kursnivån**. En *avancerad nivå*-kurs vars lärandemål bara rör sig på Minnas/Förstå-nivå indikerar att kursen ligger lägre kognitivt än nivåklassningen anger; en *grundnivå*-kurs där värdera/skapa-verb dominerar kan tyda på fellabeling eller på en kurs som egentligen tillhör avancerad nivå. Det är ett pedagogiskt och formellt problem (Bologna, examensordningen).

## Metod

`qa/check_kursplaner.py` använder ett svenskt verb-lexikon med sex revisade Bloom-nivåer (1 Minnas → 6 Skapa) som finns i [`qa/bloom_verbs.py`](../../qa/bloom_verbs.py). För varje bullet i sektionen `## Lärandemål` (svensk version) letas det **första klassbara ordet**; ledande adverb (*självständigt*, *muntligt*) saknas i lexikonet och hoppas över naturligt.

Kursnivån läses från frontmatter-fältet `niva:` (*"Grundnivå"* eller *"Avancerad nivå"*) — inte från kurskodprefix, eftersom prefix som `G2` faktiskt kan vara grundnivå.

Tre regler ger findings:

- **Bloom-nivå låg (avancerad kurs)** — `niva: "Avancerad nivå"` och inga bullets på nivå ≥ 4 (Analysera/Värdera/Skapa).
- **Bloom-nivå hög (grundkurs)** — `niva: "Grundnivå"` och ≥ 60 % av klassade bullets ligger på nivå 5–6 (Värdera/Skapa).
- **Bloom okänt verb** — ≥ 3 bullets i kursplanen vars första klassbara ord saknas i lexikonet. Inte ett kvalitetsfel, utan en signal till att utöka lexikonet.

Detalj-strängen för varje finding visar fördelningen som ett 6-cells histogram, t.ex. `fördelning [2,3,1,0,0,0]` (cell 1 = Minnas, cell 6 = Skapa).

**Begränsningar:**

- Lexikonet är handkurerat och ofullständigt — utökas iterativt utifrån `bloom-okant-verb`-fynd.
- Kontext räknas inte: *"redogöra för komplexa samband"* kan vara ett kvalificerat lärandemål trots Minnas-verbet.
- Vid dubbelplacerade verb (t.ex. *jämföra* mellan Förstå och Analysera) väljs alltid den högsta nivån.
- Endast svenska analyseras; engelska Learning Outcomes granskas inte här.

Denna analys är **manuellt kurerad** — populate-skriptet skriver in fynden, granskaren tar bort eller flaggar enligt egen bedömning.

## Datakälla

- Alla kursplaner under `0X {INST}/Kursplaner/` (IIT + IHV + IKS + ISLL)
- Endast den svenska sektionen (`## Lärandemål`)
- Kursnivå från frontmatter-fältet `niva:`

## Rekommendationer

1. **Granska varje flaggad kursplan manuellt** med kontext från syftesbeskrivning, examination och kurslitteratur.
2. **Komplettera lärandemålen med höga Bloom-verb** vid nästa revision om kontext bekräftar att kursen faktiskt ligger på avancerad nivå.
3. **Överväg nivåflyttning** om ett konsekvent mönster av låga verb finns — kursen kanske borde vara grundnivå.
