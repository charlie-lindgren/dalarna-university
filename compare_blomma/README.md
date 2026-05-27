---
title: Triangulering — vault vs Blomma (KTH/SU) vs Dalarna officiell
---

# compare_blomma — triangulering

Mappen jämför tre oberoende uppsättningar HDa-kursplaner och korslistar dem mot vårt eget arkiv över nedlagda kursplaner.

## Källor

| Källa | Antal | Beskrivning |
|-------|------:|-------------|
| **A. Dalarna officiella Excel** | 1 923 | [`supplied_by_dalarna_university_to_blomma/Aktiva kurser HDa.xlsx`](supplied_by_dalarna_university_to_blomma/Aktiva%20kurser%20HDa.xlsx) — 1 886 kurser + 37 forskarkurser. Skickad direkt från HDa till Blomma-projektet. |
| **B. Blomma `DU.json`** | 2 095 | Skrapad av Blomma-pipelinen (KTH/SU/UMU/MIUN-samarbetet) — hämtad från [amandakann/kursplansanalys](https://github.com/amandakann/kursplansanalys/blob/main/Kursplaner/DU.json) (senast uppdaterad 2026-04-14). |
| **C. Vault aktiva** | 1 939 | Min Quartz/Obsidian-vault, skrapad via [`scripts/scrape_hda_kursplaner.py`](../scripts/scrape_hda_kursplaner.py). |
| **D. Vault nedlagda-arkiv** | 7 029 | [`qa/nedlagda-kursplaner/`](../qa/nedlagda-kursplaner) — auto-uppdaterat via [`scripts/scrape_hda_nedlagda.py`](../scripts/scrape_hda_nedlagda.py). |

## Filer

```text
compare_blomma/
  supplied_by_dalarna_university_to_blomma/
    Aktiva kurser HDa.xlsx               ← officiell lista från HDa
  from_kursplansanalys_repo/
    DU.json                              ← Blommas skrapade kursplaner
    HDa.kurser.utf.csv                   ← (samma som Excelens "Kurser"-flik)
    HDa.forskarkurser.utf.csv            ← (samma som "Forskarkurser"-fliken)
    DalarnasUniversitetKurskoder.utf.csv ← Ladok-utbildningsområde per kurskod
    ladda_ned_Hogskolan_Dalarna_Web.py   ← Blommas DU-skrapare
    step1_Hogskolan_Dalarna.py           ← Blommas DU-parser → JSON
    ResultatAvSteg5_ArtikelHogreUtbildning.txt ← deras slutresultat
  triangulering.csv                      ← samlad triangulering (8 968 rader)
  triangulering.xlsx                     ← samma data + summeringsblad
  README.md
```

## Resultat

| Excel? | Blomma? | Vault aktiv? | Antal | Kategori |
|:------:|:-------:|:------------:|------:|----------|
| ✔ | ✔ | ✔ | **1 923** | `triangulerad` — finns i alla tre auktoritativa källor |
| ✖ | ✔ | ✖ | 172 | `blomma_historik_arkiverad` — alla finns i vårt nedlagda-arkiv |
| ✖ | ✖ | ✔ | 16 | `nyare_än_andra` — kurser som dykt upp på du.se efter Excel/Blomma |
| ✖ | ✖ | ✖ (men i nedlagda-arkiv) | 6 857 | `enbart_nedlagd` — historiska kursplaner i vårt arkiv |

**Totalt: 8 968 unika kurskoder.** Inga gap mot Excel eller Blomma:

- `Excel ∖ Vault aktiva = ∅` — varenda kod i HDa:s officiella aktiva-lista finns hos oss
- `Blomma ∖ (Vault aktiva ∪ Vault nedlagda) = ∅` — varenda Blomma-kod finns hos oss (antingen aktiv eller arkiverad)

## Vad var det vi hittade på vägen?

Tre buggar i våra skrapor som triangulering avslöjade:

1. **Å/Ä/Ö i kurskoder gick förlorade** i båda skraporna. Regex `code=([A-Z0-9]+)` saknade `ÅÄÖ` och plockade inte upp URL-kodade former (`%c3%85` = `Å`).
   - Fix: ny hjälpare `_extract_code_from_href` med `urllib.parse.unquote`. Effekt: +112 aktiva kurser, +585 nedlagda i arkivet.
2. **Forskarkurser saknades** — vi använde bara du.se:s vanliga kursplane-index, som inte listar forskarkurser. Forskarkurser har en egen sida ([forskarutbildningskurser](https://www.du.se/sv/forskning/forskarutbildning/forskarutbildningskurser/)).
   - Fix: ny `discover_forskarkurser()` + prefix-baserad routing (`FORSKAR_PREFIX_TO_SUBJECT`) som överskriver opålitliga `Institution`-fält på delade forskarkurspages. Effekt: +37 forskarkurser fördelade på 5 forskarämnen.
3. **AMC28N/AMC29F/AMC2AE-buggen.** Vår `scrape_course` flaggade som "nedlagd" så snart ordet *nedlagd* förekom var som helst på sidan. Det fångar metadatafältet `Nedlagd YYYY-MM-DD` (datum då kursen avvecklas) och felaktigt slänger en fullt publicerad kursplan.
   - Fix: byt detektion till du.se:s `status=discontinued`-index som auktoritativ källa.

Sammantaget: vault aktiva växte från 1 787 → 1 939 (+152), nedlagda-arkivet från 6 444 → 7 029 (+585). Total täckning: **8 968 kurskoder** med 100 % konsistens mot HDa:s Excel och Blommas dataset.

## Återstående poster — alla förväntade

- **172 historiska Blomma-poster** — Blomma sparar varje `ValidFrom`-revidering som egen post; alla 172 finns hos oss i nedlagda-arkivet under sin kurskod.
- **16 nyare vault-kurser** — kurser som skapats på du.se efter Excelens snapshot (≈ feb 2026) och Blommas senaste pull (2026-04-14). Mest `GMT3J*`/`GIE3*`/`ASV2C*` osv.

Inga av dessa är fel; de speglar bara att de tre källorna ögonblicksbilds­togs vid olika tidpunkter.
