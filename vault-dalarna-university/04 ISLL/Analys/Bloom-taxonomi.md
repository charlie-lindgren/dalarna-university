---
tags: [analys, bloom, larandemal]
up: "[[ISLL MOC]]"
status: första pass
---

# Bloom-taxonomi

## Problematiska kursplaner

<a class="download-xlsx" href="Bloom-taxonomi.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (0 rader)</span></a>

> [!example]- 0 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |

## Syfte

Lärandemålens **verbnivå bör matcha kursnivån**. Avancerade kurser (kurskod `A…` eller `G2…`) som enbart använder låga Bloom-verb (*redogöra, beskriva, identifiera*) signalerar att kursen ligger på lägre kognitiv nivå än vad nivåklassningen anger. Det är ett pedagogiskt och formellt problem (Bologna, examensordningen).

## Metod

`qa/check_kursplaner.py` markerar avancerade kurser där sektionen `## Lärandemål` innehåller **låga Bloom-verb men inga höga**.

- **Låga verb:** redogöra, beskriva, definiera, namnge, identifiera, lista, återge, ange, förklara, sammanfatta, tolka, klassificera, jämföra, känna, förstå.
- **Höga verb:** analysera, utvärdera, bedöma, kritiskt, granska, värdera, motivera, argumentera, skapa, utforma, konstruera, designa, utveckla, planera, genomföra, lösa, tillämpa, implementera, integrera, syntetisera, föreslå, reflektera, diskutera.

**Begränsningar:**

- Verb-listorna är ofullständiga — varje genomgång kan kräva utvidgning.
- Kontext räknas inte: *"redogöra för komplexa samband"* kan vara ett kvalificerat lärandemål trots det "låga" verbet.
- Endast svenska analyseras; engelska Learning Outcomes ses inte.

Denna analys är **manuellt kurerad** — populate-skriptet skriver in de rapport-genererade fynden, men granskaren tar bort eller flaggar enligt egen bedömning.

## Datakälla

- Alla kursplaner under `0X {INST}/Kursplaner/` med kurskod som börjar med `A` eller `G2` (avancerad nivå)
- Endast den svenska sektionen (`## Lärandemål`)

## Resultat

*Fylls i efter första genomgång.*

## Observationer

*Fylls i efter första genomgång.*

## Rekommendationer

1. **Granska varje flaggad kursplan manuellt** med kontext från syftesbeskrivning, examination och kurslitteratur.
2. **Komplettera lärandemålen med höga Bloom-verb** vid nästa revision om kontext bekräftar att kursen faktiskt ligger på avancerad nivå.
3. **Överväg nivåflyttning** om ett konsekvent mönster av låga verb finns — kursen kanske borde vara grundnivå.
