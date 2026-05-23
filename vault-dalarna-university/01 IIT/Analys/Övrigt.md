---
tags: [analys, ovrigt]
up: "[[IIT MOC]]"
status: första pass
---

# Övrigt

## Problematiska kursplaner

> [!example]- 0 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |

## Syfte

Sektionen `## Övrigt` innehåller dels kursspecifik information (samläsning, ersätter äldre kurser, examensbegränsningar), dels en standardfras om **riktat pedagogiskt stöd från Högskolan Dalarna**. Standardfrasen är central för studenter med funktionsnedsättning som behöver anpassad examination — när den saknas eller är formulerad annorlunda i en kursplan blir det otydligt vilka anpassningsmöjligheter som gäller. Syftet med analysen är att kartlägga **var Övrigt-sektionen saknas helt och var standardfrasen om pedagogiskt stöd inte finns med**.

## Metod

Sektionen `## Övrigt` extraheras från den svenska sidan. Två mönster flaggas:

1. **Sektion saknas** — ingen `## Övrigt` finns i kursplanen.
2. **Saknar standardfras om pedagogiskt stöd** — sektionen finns men innehåller inte ankarfrasen *"pedagogiskt stöd från Högskolan Dalarna"*. Den fullständiga standardfrasen lyder ungefär: *"Om studenten har ett beslut/rekommendation om riktat pedagogiskt stöd från Högskolan Dalarna på grund av funktionsnedsättning, har examinator rätt att anpassa examinationen. Examinator avgör utifrån kursplanens mål om examinationen kan anpassas i enlighet med beslutet/rekommendationen."*

Analysen flaggar både kursplaner där frasen helt saknas och kursplaner med avvikande formuleringar — eventuella legitima varianter (t.ex. nyare formuleringar antagna av institutionen) bör i så fall normaliseras gemensamt över alla institutioner.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna.
- Endast den svenska sektionen `## Övrigt`.

## Rekommendationer

1. **Lägg till Övrigt-sektion** i kursplaner som saknar den helt — minst med standardfrasen om pedagogiskt stöd.
2. **Harmonisera formuleringen om pedagogiskt stöd** — använd den etablerade frasen exakt eller anta en gemensam reviderad formulering över alla fyra institutioner.
3. **Behåll kursspecifik information** (samläsning, ersätter, uppdragsutbildning) — flaggan gäller endast standardfrasen, övrigt innehåll i sektionen påverkas inte.
4. **Lyft frågan i berörda kvalitetsutskott** — bör HDa centralt fastställa en mall för Övrigt-sektionen så att standardfrasen alltid finns med vid nyutveckling och revidering?
