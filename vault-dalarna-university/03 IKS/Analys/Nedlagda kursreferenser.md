---
tags: [analys, nedlagda-referenser]
up: "[[IKS Analys MOC]]"
status: första pass
---

# Nedlagda kursreferenser

## Problematiska utbildningsplaner

<a class="download-xlsx" href="03-IKS/Analys/Nedlagda-kursreferenser.xlsx" download><svg class="download-xlsx-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="7 10 12 15 17 10"/><line x1="12" y1="15" x2="12" y2="3"/></svg><span>Ladda ner som Excel-fil (11 rader)</span></a>

> [!example]- 11 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |
> | [HFRIG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=HFRIG) | Utbildningsplan | Programmet listar nedlagd kurs | `Det cinematiska språket: Mise-en-scène` → `BQ1088` (nedlagd 2025-03-06) — plain-text-referens; rad: - Det cinematiska språket: Mise-en-scène, 15 hp |
> | [KFTKG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=KFTKG) | Utbildningsplan | Programmet listar nedlagd kurs | `Manus för TV och film 2. Dramaturgi, genre och filmhistoria` → `BQ1050` (nedlagd 2014-05-06) — plain-text-referens; rad: - Manus för TV och film 2. Dramaturgi, genre och filmhistoria, 15 hp |
> | [KFTPG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=KFTPG) | Utbildningsplan | Programmet listar nedlagd kurs | `Konceptutveckling inom medieproduktion` → `BQ2049` (nedlagd 2025-03-06) — plain-text-referens; rad: - Konceptutveckling inom medieproduktion, 7,5 hp |
> | [LBF3A](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=LBF3A) | Utbildningsplan | Programmet listar nedlagd kurs | `Text, kommunikation och lärande i en mångkulturell skola` → `GSV22L` (nedlagd 2024-10-11) — plain-text-referens; rad: - Text, kommunikation och lärande i en mångkulturell skola, 15 hp |
> | [LP79A](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=LP79A) | Utbildningsplan | Programmet listar nedlagd kurs | `Didaktik och ledarskap för ämneslärare` → `PG1020` (nedlagd 2018-07-02) — plain-text-referens; rad: - Didaktik och ledarskap för ämneslärare, 15 hp |
> | [LPGYA](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=LPGYA) | Utbildningsplan | Programmet listar nedlagd kurs | `Didaktik och ledarskap för ämneslärare` → `PG1020` (nedlagd 2018-07-02) — plain-text-referens; rad: - Didaktik och ledarskap för ämneslärare, 15 hp |
> | [SSHVG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=SSHVG) | Utbildningsplan | Programmet listar nedlagd kurs | `Samhällsekonomi` → `GSQ25R` (nedlagd 2025-12-08) — plain-text-referens; rad: - Samhällsekonomi, 7,5 hp |
> | [SSHVG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=SSHVG) | Utbildningsplan | Programmet listar nedlagd kurs | `Konformitet och avvikelse` → `SO1007` (nedlagd 2025-11-13) — plain-text-referens; rad: - Konformitet och avvikelse, 7,5 hp |
> | [STMGG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=STMGG) | Utbildningsplan | Programmet listar nedlagd kurs | `Grundläggande ekonomistyrning` → `FEA034` (nedlagd 2008-03-18) — plain-text-referens; rad: - Grundläggande ekonomistyrning, 7,5 hp |
> | [STMGG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=STMGG) | Utbildningsplan | Programmet listar nedlagd kurs | `Kvalitativa forskningsmetoder` → `SB3002` (nedlagd 2013-01-15) — plain-text-referens; rad: - Kvalitativa forskningsmetoder, 7,5 hp |
> | [STMGG](https://www.du.se/sv/utbildning/Program/utbildningsplan/?code=STMGG) | Utbildningsplan | Programmet listar nedlagd kurs | `Projektarbete` → `BTA009` (nedlagd 2008-05-22) — plain-text-referens; rad: - Projektarbete, 15 hp |

## Syfte

Sektionen *Programmets kurser* i en utbildningsplan listar de kurser som ingår i programmet. När en kurs på du.se markeras som nedlagd försvinner den ur HDa:s aktiva katalog, men utbildningsplanens text uppdateras inte automatiskt — kvar blir referenser till kurser som inte längre erbjuds. Syftet med analysen är att kartlägga **vilka utbildningsplaner som fortfarande listar nedlagda kurser** så att texten kan revideras innan studenter förlitar sig på en inaktuell kursförteckning.

## Metod

`qa/check_utbildningsplaner.py` parsar varje utbildningsplans `## 3. Programmets kurser`-sektion och plockar ut kursbullets i tre former: `[[CODE|Namn]]`-wikilänk, `<a class="no-graph" href="CODE">…</a>` (korsinstitutionell länk) och oklassad text (kursnamn utan kursplankodsmatchning). Varje träff slås upp mot QA-cachen i `qa/nedlagda-kursplaner/` — antingen via kurskod (för länkar) eller via namnnormalisering (för plain-text-bullets). En träff betyder att den listade kursen har `status=discontinued` på du.se och därför inte längre kan läsas.

## Datakälla

- Samtliga utbildningsplaner i `0X {INST}/Utbildningsplaner/`.
- QA-cache av nedlagda kursplaner: `qa/nedlagda-kursplaner/` (skrapas via menyval 7 i `hda.sh`).

## Rekommendationer

1. **Byt referens till ersättningskursen** — när en nedlagd kurs har en aktuell efterträdare (samma huvudområde, samma omfattning) uppdateras utbildningsplanens kurslista till den nya koden/namnet.
2. **Stryk kursen ur programmet** — när det inte finns en ersättare och kursen inte längre är avgörande för examensmålen, ta bort referensen och justera programmets totala omfattning vid behov.
3. **Lyft till programansvarig** — utbildningsplanens kurslista är ett beslut för programansvarig; QA-rapporten visar var ändringar behövs men inte vilken väg som är rätt.
