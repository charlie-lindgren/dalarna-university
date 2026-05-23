---
tags: [analys, terminologi, sprak]
up: "[[IIT MOC]]"
status: första pass
---

# Terminologi

## Problematiska kursplaner

> [!example]- 0 fynd — klicka för att expandera
>
> | Kursplan | Ämne | Problem | Detalj |
> | --- | --- | --- | --- |

## Syfte

Konsekvent terminologi inom samma kursplan stöder läsbarhet och visar redaktionell omsorg. Vid HDa förekommer två klassiska blandningar inom den svenska delen av kursplanerna:

- *studenten* vs *den studerande* — två etablerade benämningar på samma roll. Stilguider rekommenderar att man väljer en och håller sig till den genom hela dokumentet.
- *ska* vs *skall* — *skall* är en ålderdomlig variant som de flesta moderna språkriktlinjer rekommenderar att man ersätter med *ska*.

Syftet med analysen är att kartlägga **vilka kursplaner som blandar dessa varianter inom samma dokument**, så att harmonisering kan ske vid nästa revidering.

## Metod

För varje kursplan extraheras allt textinnehåll utom frontmatter och `## English Version`. Två mönster flaggas oberoende av varandra:

1. **Blandar 'studenten' och 'den studerande'** — båda förekommer minst en gång var som hela ord (inte som del av andra ord).
2. **Blandar 'ska' och 'skall'** — båda förekommer minst en gång var som hela ord.

Kursplaner som konsekvent använder *bara* en variant flaggas inte — denna analys gäller endast intern inkonsekvens, inte val mellan varianterna.

## Datakälla

- Samtliga kursplaner från du.se vid Högskolan Dalarna.
- Hela den svenska delen (alla sektioner utom `## English Version`).

## Rekommendationer

1. **Välj en variant per kursplan** — *studenten* respektive *ska* är de mest använda och rekommenderas i moderna stilguider, men det viktiga är att samma val gäller genom hela dokumentet.
2. **Använd sök-och-ersätt** vid revidering — eftersom det rör hela ord (med ordgränser) är ersättningen mekaniskt enkel.
3. **Lyft frågan i berörda kvalitetsutskott** — bör institutionerna ha gemensamma terminologival för nyutveckling, eller är det upp till varje kursansvarig?
