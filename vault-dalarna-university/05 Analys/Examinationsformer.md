---
tags: [analys, examination]
up: "[[Analys MOC]]"
status: första pass
---

# Examinationsformer

## Problematiska kursplaner

<a class="download-xlsx" href="Examinationsformer.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (0 rader)</span></a>

> [!example]- 0 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |

## Syfte

Säkerställa att hp-vikterna på betygsskalans **delmoment** (i sektionen `## Betyg`) summerar till kursens totala hp-värde. En felaktig summa tyder på att ett moment lagts till eller tagits bort utan att de övriga justerats.

## Metod

`qa/check_kursplaner.py` läser kursens hp från frontmatter, extraherar alla `X hp`-värden i bullet-rader i `## Betyg`-sektionen och flaggar filer där absolutavvikelsen överstiger 0,1 hp.

**Begränsningar:** Kurser utan hp-specifikation per delmoment i Betyg-sektionen flaggas inte (kan vara legitimt). Manuell granskning krävs för att skilja scraping-artefakter från verkliga datafel.

## Datakälla

- Alla kursplaner under `0X {INST}/Kursplaner/` (IIT + IHV + IKS + ISLL)
- Endast sektionen `## Examinationsformer`

## Resultat

*Fylls i efter första genomgång.*

## Observationer

*Fylls i efter första genomgång.*

## Rekommendationer

1. **Lägg till Ladok-kod för varje delmoment** vid nästa revision av flaggade kursplaner.
2. **Vid endast ett delmoment** — använd ändå en bullet och ange koden, så att formatet är förutsägbart.
3. **Diskutera med Ladok-administratör** om det finns kursplaner där examinationskoden medvetet utelämnas av rättvise- eller historiska skäl.
