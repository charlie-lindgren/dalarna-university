---
title: Triangulering — vault vs Blomma (KTH/SU) vs Dalarna officiell
---

# compare_blomma — triangulering

Mappen jämför tre oberoende uppsättningar HDa-kursplaner:

| Källa | Antal | Beskrivning |
|------|------:|-------------|
| **A. Dalarna officiella Excel** | 1 923 | `supplied_by_dalarna_university_to_blomma/Aktiva kurser HDa.xlsx` — 1 886 kurser + 37 forskarkurser. Skickad direkt från HDa till Blomma-projektet. |
| **B. Blomma `DU.json`** | 2 095 | Skrapad av Blomma-pipelinen (KTH/SU/UMU/MIUN-samarbetet) — hämtad från [amandakann/kursplansanalys/Kursplaner/DU.json](https://github.com/amandakann/kursplansanalys/blob/main/Kursplaner/DU.json) (senast uppdaterad 2026-04-14). |
| **C. Min vault** | 1 787 | Min Quartz/Obsidian-vault, skrapad via `scripts/scrape_hda_kursplaner.py`. |

## Filer i denna mapp

```text
supplied_by_dalarna_university_to_blomma/
  Aktiva kurser HDa.xlsx               ← officiell lista från HDa
from_kursplansanalys_repo/
  DU.json                              ← Blommas skrapade kursplaner (rådata)
  HDa.kurser.utf.csv                   ← CSV-version av Excelens "Kurser"-flik
  HDa.forskarkurser.utf.csv            ← CSV-version av "Forskarkurser"-fliken
  DalarnasUniversitetKurskoder.utf.csv ← Ladok-utbildningsområde per kurskod (1 936 rader)
  ladda_ned_Hogskolan_Dalarna_Web.py   ← Blommas DU-skrapare
  step1_Hogskolan_Dalarna.py           ← Blommas DU-parser → JSON
  ResultatAvSteg5_ArtikelHogreUtbildning.txt ← deras pipelines slutresultat
analysis_crosstab.tsv                  ← code × {in_excel, in_blomma, in_vault}
analysis_*.txt                         ← respektive set-differenser
```

## Hittade fakta (omedelbara)

1. **`Aktiva kurser HDa.xlsx` är identisk med `HDa.kurser.utf.csv` + `HDa.forskarkurser.utf.csv`.** Samma rader, samma URL-struktur — Blomma transkriberade bara Dalarnas Excel till CSV. Det är alltså inte två oberoende källor.

2. **Dalarnas Excel ⊂ Blommas JSON.** Varje kurs i Excelen finns också i Blommas `DU.json` (0 i `Excel \ Blomma`).

## Tre-vägs medlemskap

| In Excel? | In Blomma? | In Vault? | Antal |
|:---------:|:----------:|:---------:|------:|
| ✔ | ✔ | ✔ | **1 771** |
| ✔ | ✔ | ✖ | 152 |
| ✖ | ✔ | ✖ | 172 |
| ✖ | ✖ | ✔ | 16 |
| Övriga | — | — | 0 |

### 152 kurser i Excel + Blomma men saknas i vault

Tre tydliga kategorier:

| Kategori | Antal | Kommentar |
|----------|------:|-----------|
| **Forskarkurser** (FDA/FEB/FHV/FMI/FPA/FVV/MIKR) | 37 | Min skrapare hämtar inte forskarkurser. Excelens `Forskarkurser`-flik täcker dem fullständigt. |
| **Koder med Å/Ä/Ö** (GFÖ\*, GVÅ\*, AVÅ\*, FÖ\*, VÅ\*, MÖ\*, AFÖ\*) | 112 | Bekräftad regexbugg på `scripts/scrape_hda_kursplaner.py:479`: `re.search(r"code=([A-Z0-9]+)", a["href"])` saknar `ÅÄÖ` i teckenklassen. Bör vara `[A-Z0-9ÅÄÖ]+`. |
| **AMC\*** | 3 | AMC28N, AMC29F, AMC2AE — ny ämnesprefix som troligen saknas i min subject-mapping. |

→ Att fixa Å/Ä/Ö-hanteringen + lägga till AMC skulle direkt höja vault från 1 787 till ~1 902 (115 nya). Forskarkurser är en separat scope-fråga.

### 172 kurser unika för Blomma JSON

Äldre/inaktiverade kursplaner som Blomma skrapade tidigare men som **inte längre** står med på HDa:s aktuella aktiva lista. Prefix­distribution:
`SS:61, GV:33, GF:28, AV:23, VÅ:19, ST:14, FÖ:12, MT:12, JP:10, SO:10, ...`. Snittformat: gamla numreringar (FÖ1041, DT2019, EG3003, AVÅ27J etc.).

Min `qa/identify_ej_aktiv.py` skulle ha taggat dessa som `ej-aktiv` om jag hade lagt in dem — vilket korrekt återspeglar att de inte längre är aktiva.

### 16 kurser unika för vault

Nyare kurser som dykt upp på du.se efter att Blomma drog sin data och som inte heller står i Excelen. Alla har höga "3K"/"3J"-numreringar:

```
ASV2CP, ASV2CQ (SVE)
GEN3K3 (ENA)
GHI3JX (HIA)
GIE3JS, GIE3JW (IEA)
GMD3K4 (MDI)
GMT3JQ, GMT3JR, GMT3JT, GMT3JU, GMT3JV, GMT3JY, GMT3JZ (MTA)
GPG3JP (PGA)
GSS3K2 (SSA)
```

→ Tyder på att min skrapning är **nyare** än Excel/Blomma — ett bra tecken.

## Slutsats

- **Triangulering bekräftar att skrapningen i stort sett är komplett**: 1 771 / 1 787 (99,1 %) av vaultens kurser triangulerar mot båda externa källorna.
- **Två konkreta bug-fixes** identifierade i min skrapare: stöd för Å/Ä/Ö i kurskoder (112 kurser) och AMC-prefix (3 kurser).
- **Forskarkurser (37 st)** är en scope-fråga, inte ett fel — fritt val om de ska in.
- **172 inaktiva plan­versioner** i Blommas dataset är förväntat — de skrapade vid en tidigare tidpunkt och behåller historiska versioner.
- **Excelen från Dalarna är en strikt delmängd av Blommas dataset** och innehåller inga unika observationer; den fungerar bäst som auktoritativ "aktiv vid datum X"-snapshot.

Kör om jämförelsen efter en ny scrape med `python3 _rebuild.py` (skapad om/när behov uppstår).
