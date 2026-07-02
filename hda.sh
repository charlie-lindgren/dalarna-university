#!/usr/bin/env bash
# hda.sh — Meny för Högskolan Dalarna kvalitetsarbetsflöde
# Kör från repo-roten: ./hda.sh

set -euo pipefail
cd "$(dirname "$0")"

# Föredra .venv om den finns, annars systemets python3.
if [[ -x ".venv/bin/python" ]]; then
    PYTHON="${PYTHON:-.venv/bin/python}"
else
    PYTHON="${PYTHON:-python3}"
fi

RAPPORT_DIR="qa/rapporter"
RAPPORT_DIR_UTB="qa/rapporter-utb"

# ── färger ──────────────────────────────────────────────────────────────────
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
MAGENTA='\033[0;35m'
RESET='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${CYAN}${BOLD}  Högskolan Dalarna — Plananalys${RESET}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "  Python: ${PYTHON}"
    echo ""
}

print_menu() {
    echo -e "  ${MAGENTA}${BOLD}Komplett pipeline${RESET}"
    echo -e "    ${BOLD}1.${RESET}  ${BOLD}Kör allt${RESET} — skrapa + QC + bygg till public/"
    echo ""
    echo -e "  ${MAGENTA}${BOLD}Skrapa${RESET}"
    echo -e "    ${BOLD}2.${RESET}  Skrapa ALLA kursplaner (inkl. strö-/orphan-koder)"
    echo -e "    ${BOLD}3.${RESET}  Skrapa kursplaner (endast ordinarie ämnen)"
    echo -e "    ${BOLD}4.${RESET}  Skrapa utbildningsplaner"
    echo -e "    ${BOLD}5.${RESET}  Identifiera vilande kursplaner"
    echo -e "    ${BOLD}6.${RESET}  Bygg om MOC-filer från vault"
    echo -e "    ${BOLD}7.${RESET}  ${BOLD}Kör alla skrapa-steg${RESET} (2 + 4 + 5 + 6)"
    echo ""
    echo -e "  ${MAGENTA}${BOLD}QA-cache${RESET}"
    echo -e "    ${BOLD}8.${RESET}  Skrapa nedlagda kursplaner (qa/nedlagda-kursplaner/, ej i vault)"
    echo ""
    echo -e "  ${MAGENTA}${BOLD}Kvalitetsgranskning${RESET}"
    echo -e "    ${BOLD}9.${RESET}  QA kursplaner (rapport)"
    echo -e "   ${BOLD}10.${RESET}  QA utbildningsplaner (rapport)"
    echo -e "   ${BOLD}11.${RESET}  Jämför kursplan-rapporter (lösta/nya fynd)"
    echo -e "   ${BOLD}12.${RESET}  Populera analysfilerna + plan-callouts (kurs/utb, från senaste rapport)"
    echo -e "   ${BOLD}13.${RESET}  Rensa analysfilerna (ta bort lösta fynd)"
    echo -e "   ${BOLD}14.${RESET}  ${BOLD}Kör alla QC-steg${RESET} (9 + 10 + 12)"
    echo ""
    echo -e "  ${MAGENTA}${BOLD}Bygg & publicera${RESET}"
    echo -e "   ${BOLD}15.${RESET}  ${BOLD}Publicera sajten online${RESET} (commit + push → GitHub Pages)"
    echo -e "   ${BOLD}16.${RESET}  Bygg & förhandsvisa sajten lokalt"
    echo ""
    echo -e "    ${BOLD}q.${RESET}  Avsluta"
    echo ""
}

prompt_apply_mode() {
    # Alla körningar är "apply" — inga dry-runs och inga interaktiva prompts.
    APPLY_FLAG="--apply"
}

# ── steg: skrapa allt (inkl. strökoder) ─────────────────────────────────────
run_scrape_all() {
    echo -e "${BOLD}Skrapa ALLA kursplaner från du.se${RESET}"
    echo ""
    echo "Detta tar fram alla aktiva kursplaner (även vilande) på du.se,"
    echo "inklusive strö-/orphan-koder som inte syns i ämnes- eller"
    echo "programlistan. Källan är du.se:s fullständiga kursplan-index"
    echo "(ett enda anrop), och nedlagda kursplaner filtreras bort där."
    echo ""
    echo -e "${YELLOW}Skrapan parallelliseras (concurrency=6) — typiskt ett par minuter.${RESET}"
    echo ""

    prompt_apply_mode

    echo ""
    echo -e "${YELLOW}Kör scrape --discover-stray ${APPLY_FLAG} …${RESET}"
    # shellcheck disable=SC2086
    "$PYTHON" scripts/scrape_hda_kursplaner.py \
        --discover-stray \
        $APPLY_FLAG

    echo ""
    echo -e "${GREEN}✓ Fullständig kursplan-skrapning klar${RESET}"
    if [[ -n "$APPLY_FLAG" && -z "${BATCH_APPLY_FLAG+x}" ]]; then
        echo "  Tips: kör menyval 5 för att tagga vilande kursplaner."
    fi
}

# ── steg: skrapning kursplaner (utan stray) ─────────────────────────────────
run_scrape_kurs() {
    echo -e "${BOLD}Skrapa kursplaner (ordinarie ämnen)${RESET}"
    echo ""
    prompt_apply_mode
    echo ""
    echo -e "${YELLOW}Kör scrape ${APPLY_FLAG} …${RESET}"
    # shellcheck disable=SC2086
    "$PYTHON" scripts/scrape_hda_kursplaner.py $APPLY_FLAG
    echo -e "${GREEN}✓ Kursplan-skrapning klar${RESET}"
}

# ── steg: skrapning utbildningsplaner ───────────────────────────────────────
run_scrape_utb() {
    echo -e "${BOLD}Skrapa utbildningsplaner${RESET}"
    echo ""
    prompt_apply_mode
    echo ""
    echo -e "${YELLOW}Kör scrape ${APPLY_FLAG} …${RESET}"
    # shellcheck disable=SC2086
    "$PYTHON" scripts/scrape_hda_utbildningsplaner.py $APPLY_FLAG
    echo -e "${GREEN}✓ Utbildningsplan-skrapning klar${RESET}"
}

# ── steg: skrapa nedlagda kursplaner (QA-cache) ─────────────────────────────
run_scrape_nedlagda() {
    echo -e "${BOLD}Skrapa nedlagda kursplaner${RESET}"
    echo ""
    echo "Hämtar alla kursplaner med status=discontinued från du.se och"
    echo "sparar en slim metadatafil per kod i qa/nedlagda-kursplaner/."
    echo "Cachen är gitignored och visas inte på sajten — den används av"
    echo "QA-koden (för att flagga nedlagda kursreferenser i utbildnings-"
    echo "planer och vid analys av förkunskapskrav)."
    echo ""
    echo -e "${YELLOW}Cirka 6500 kurser; ett par minuter vid första körningen.${RESET}"
    echo "Befintliga cache-poster hoppas över automatiskt vid omkörning."
    echo ""
    prompt_apply_mode
    echo ""
    # shellcheck disable=SC2086
    "$PYTHON" scripts/scrape_hda_nedlagda.py $APPLY_FLAG
    echo -e "${GREEN}✓ Nedlagda-cache uppdaterad${RESET}"
}

# ── steg: identifiera vilande kursplaner ────────────────────────────────────
run_vilande() {
    echo -e "${BOLD}Identifiera vilande kursplaner${RESET}"
    echo ""
    echo "Jämför vault mot du.se och taggar kurser utan aktiv kursomgång som"
    echo "vilande (uppdaterar även 0X {INST}/Analys/Vilande kursplaner.md/.xlsx)."
    echo ""
    prompt_apply_mode
    echo ""
    # shellcheck disable=SC2086
    "$PYTHON" qa/identify_ej_aktiv.py $APPLY_FLAG
}

# ── steg: bygg om MOC-filerna från vault-tillstånd ──────────────────────────
run_rebuild_mocs() {
    echo -e "${BOLD}Bygg om MOC-filer från vault${RESET}"
    echo ""
    echo "Skannar vault-dalarna-university/ och regenererar samtliga ämnes-MOC:s"
    echo "och institutions-MOC:s från frontmatter. Migrerar även forskarkurser"
    echo "till 'Forskarämne X'-namn så att grund- och forskarämnen får separata"
    echo "MOC-filer (löser kollisioner som annars uppstår i grafvyn)."
    echo ""
    prompt_apply_mode
    echo ""
    # shellcheck disable=SC2086
    "$PYTHON" qa/rebuild_mocs.py $APPLY_FLAG
}

# ── steg: kör alla skrapa-steg i sekvens ────────────────────────────────────
run_scrape_pipeline() {
    echo -e "${BOLD}Kör alla skrapa-steg${RESET}"
    echo ""
    echo "Kör i sekvens:"
    echo "  • Skrapa ALLA kursplaner (inkl. strö-/orphan-koder)"
    echo "  • Skrapa utbildningsplaner"
    echo "  • Identifiera vilande kursplaner"
    echo "  • Bygg om MOC-filer från vault"
    echo ""
    prompt_apply_mode
    BATCH_APPLY_FLAG="$APPLY_FLAG"
    echo ""
    run_scrape_all
    echo ""
    run_scrape_utb
    echo ""
    run_vilande
    echo ""
    run_rebuild_mocs
    unset BATCH_APPLY_FLAG
    echo ""
    echo -e "${GREEN}✓ Alla skrapa-steg klara${RESET}"
}

# ── steg: bygg Quartz-sajten ────────────────────────────────────────────────
run_build_site() {
    echo -e "${BOLD}Bygg Quartz-sajten${RESET}"
    echo ""
    if [[ ! -d node_modules ]]; then
        echo -e "${YELLOW}node_modules saknas — kör npm ci först …${RESET}"
        npm ci
    fi
    echo -e "${YELLOW}Kör npx quartz build …${RESET}"
    npx quartz build
    echo -e "${GREEN}✓ Sajten byggd till public/${RESET}"
}

# ── steg: bygg & förhandsvisa ───────────────────────────────────────────────
run_serve_site() {
    echo -e "${BOLD}Bygg & förhandsvisa sajten${RESET}"
    echo ""
    if [[ ! -d node_modules ]]; then
        echo -e "${YELLOW}node_modules saknas — kör npm ci först …${RESET}"
        npm ci
    fi
    echo -e "${YELLOW}Kör npx quartz build --serve (Ctrl-C för att avsluta) …${RESET}"
    npx quartz build --serve
}

# ── steg: publicera sajten online ───────────────────────────────────────────
# Uppdaterar den LIVE-sajten. Ett lokalt bygge (15 tidigare / 16) rör inte
# online-sidan — den byggs bara av GitHub Actions vid push till main. Denna
# funktion gör därför en kontroll-build, committar + pushar, vilket startar
# deployen. Finns inga ändringar startas en ny deploy manuellt (workflow_dispatch).
run_publish_site() {
    echo -e "${BOLD}Publicera sajten online${RESET}"
    echo ""
    if [[ ! -d node_modules ]]; then
        echo -e "${YELLOW}node_modules saknas — kör npm ci först …${RESET}"
        npm ci
    fi
    echo -e "${YELLOW}Kontroll-bygge lokalt (npx quartz build) …${RESET}"
    if ! npx quartz build; then
        echo -e "${RED}✗ Bygget misslyckades — inget publiceras. Åtgärda felen ovan först.${RESET}"
        return 1
    fi
    echo -e "${GREEN}✓ Lokalt bygge OK${RESET}"
    echo ""
    if [[ -n "$(git status --porcelain)" ]]; then
        git add -A
        default_msg="Uppdatera sajten $(date +%Y-%m-%d)"
        read -rp "Commit-meddelande [$default_msg]: " msg
        msg="${msg:-$default_msg}"
        git commit -m "$msg"
        echo -e "${YELLOW}Pushar till main (startar deployen) …${RESET}"
        git push origin main
    else
        echo -e "${YELLOW}Inga ändringar att committa — startar en ny deploy manuellt …${RESET}"
        if ! gh workflow run deploy.yml --ref main; then
            echo -e "${RED}✗ Kunde inte starta deployen (kräver 'gh' inloggad).${RESET}"
            return 1
        fi
    fi
    echo ""
    echo -e "${GREEN}✓ Deploy startad.${RESET} Sajten uppdateras när körningen blir grön (~5–8 min)."
    echo -e "   Följ den här: ${BOLD}https://github.com/charlie-lindgren/dalarna-university/actions${RESET}"
}

# ── steg: QA kursplaner ─────────────────────────────────────────────────────
run_qa_kurs() {
    echo -e "${BOLD}QA kursplaner${RESET}"
    echo ""

    TODAY="$(date +%Y-%m-%d-%H%M)"
    OUTFILE="${RAPPORT_DIR}/rapport-${TODAY}.md"
    mkdir -p "$RAPPORT_DIR"

    if ! command -v hunspell &>/dev/null; then
        echo -e "${YELLOW}Varning: hunspell hittades inte — stavningskontroll hoppas över.${RESET}"
        SKIP_HUNSPELL="--skip-hunspell"
    else
        SKIP_HUNSPELL=""
    fi

    echo -e "${YELLOW}Kör QA-kontroller …${RESET}"
    # shellcheck disable=SC2086
    "$PYTHON" qa/check_kursplaner.py $SKIP_HUNSPELL --out "$OUTFILE"

    echo ""
    echo -e "${GREEN}✓ QA-rapport sparad: ${BOLD}${OUTFILE}${RESET}"
    if [[ -z "${BATCH_APPLY_FLAG+x}" ]]; then
        echo ""
        echo "  Nästa steg: kör menyval 12 för att populera analysfilerna i varje institutions Analys-mapp."
    fi
}

# ── steg: QA utbildningsplaner ──────────────────────────────────────────────
run_qa_utb() {
    echo -e "${BOLD}QA utbildningsplaner${RESET}"
    echo ""

    TODAY="$(date +%Y-%m-%d-%H%M)"
    OUTFILE="${RAPPORT_DIR_UTB}/rapport-${TODAY}.md"
    mkdir -p "$RAPPORT_DIR_UTB"

    if ! command -v hunspell &>/dev/null; then
        echo -e "${YELLOW}Varning: hunspell hittades inte — stavningskontroll hoppas över.${RESET}"
        SKIP_HUNSPELL="--skip-hunspell"
    else
        SKIP_HUNSPELL=""
    fi

    echo -e "${YELLOW}Kör QA-kontroller …${RESET}"
    # shellcheck disable=SC2086
    "$PYTHON" qa/check_utbildningsplaner.py $SKIP_HUNSPELL --out "$OUTFILE"

    echo ""
    echo -e "${GREEN}✓ QA-rapport sparad: ${BOLD}${OUTFILE}${RESET}"
}

# ── steg: jämför rapporter ───────────────────────────────────────────────────
run_diff() {
    echo -e "${BOLD}Jämför kursplan-rapporter${RESET}"
    echo ""

    RAPPORTER=()
    while IFS= read -r f; do
        RAPPORTER+=("$f")
    done < <(ls -1 "${RAPPORT_DIR}"/rapport-*.md 2>/dev/null | sort)
    COUNT=${#RAPPORTER[@]}

    if (( COUNT < 2 )); then
        echo -e "${YELLOW}Minst 2 rapporter krävs för jämförelse. Kör en QA-rapport först.${RESET}"
        return
    fi

    echo "Tillgängliga rapporter:"
    for i in "${!RAPPORTER[@]}"; do
        echo "  $((i+1)). $(basename "${RAPPORTER[$i]}")"
    done
    echo ""
    echo -e "${CYAN}Tryck Enter för att jämföra de två senaste, eller ange nummer (t.ex. 1 3):${RESET}"
    read -rp "Val [Enter = senaste två]: " selection
    echo ""

    if [[ -z "$selection" ]]; then
        OLD="${RAPPORTER[$((COUNT-2))]}"
        NEW="${RAPPORTER[$((COUNT-1))]}"
    else
        read -r idx_old idx_new <<< "$selection"
        OLD="${RAPPORTER[$((idx_old-1))]}"
        NEW="${RAPPORTER[$((idx_new-1))]}"
    fi

    "$PYTHON" qa/diff_rapporter.py "$OLD" "$NEW"
}

# ── steg: populera analysfilerna ────────────────────────────────────────────
run_populate() {
    echo -e "${BOLD}Populera analysfilerna + plan-callouts${RESET}"
    echo ""
    echo "Fyller varje institutions analysfiler från senaste rapporten och"
    echo "skriver en plan-specifik dropdown överst i varje kurs- och"
    echo "utbildningsplan med fynd (tar bort den från planer utan kvarvarande"
    echo "fynd). Varje plan får bara de fynd vars kod matchar planen."
    echo ""
    "$PYTHON" qa/populate_analysfiler.py
}

# ── steg: rensa analysfilerna ───────────────────────────────────────────────
run_prune() {
    echo -e "${BOLD}Rensa analysfilerna${RESET}"
    echo ""
    "$PYTHON" qa/prune_analysfiler.py
}

# ── steg: kör alla QC-steg i sekvens ────────────────────────────────────────
run_qc_pipeline() {
    echo -e "${BOLD}Kör alla QC-steg${RESET}"
    echo ""
    echo "Kör i sekvens:"
    echo "  • QA kursplaner (rapport)"
    echo "  • QA utbildningsplaner (rapport)"
    echo "  • Populera analysfilerna från senaste rapport"
    echo ""
    prompt_apply_mode
    BATCH_APPLY_FLAG="$APPLY_FLAG"
    echo ""
    run_qa_kurs
    echo ""
    run_qa_utb
    echo ""
    run_populate
    unset BATCH_APPLY_FLAG
    echo ""
    echo -e "${GREEN}✓ Alla QC-steg klara${RESET}"
}

# ── steg: hela pipelinen ────────────────────────────────────────────────────
run_full_pipeline() {
    echo -e "${BOLD}Komplett pipeline — skrapa + QC + bygg${RESET}"
    echo ""
    echo "Kör i sekvens:"
    echo "  • Skrapa ALLA kursplaner (inkl. strö-/orphan-koder)"
    echo "  • Skrapa utbildningsplaner"
    echo "  • Identifiera vilande kursplaner"
    echo "  • Bygg om MOC-filer från vault"
    echo "  • Skrapa nedlagda kursplaner (QA-cache)"
    echo "  • QA kursplaner (rapport)"
    echo "  • QA utbildningsplaner (rapport)"
    echo "  • Populera analysfilerna"
    echo "  • Bygg Quartz-sajten till public/"
    echo ""
    prompt_apply_mode
    BATCH_APPLY_FLAG="$APPLY_FLAG"
    echo ""
    run_scrape_all
    echo ""
    run_scrape_utb
    echo ""
    run_vilande
    echo ""
    run_rebuild_mocs
    echo ""
    run_scrape_nedlagda
    echo ""
    run_qa_kurs
    echo ""
    run_qa_utb
    echo ""
    run_populate
    unset BATCH_APPLY_FLAG
    echo ""
    run_build_site
    echo ""
    echo -e "${GREEN}✓ Komplett pipeline klar${RESET}"
}

print_header
while true; do
    print_menu
    read -rp "Val: " choice
    echo ""
    case "$choice" in
        1)  run_full_pipeline ;;
        2)  run_scrape_all ;;
        3)  run_scrape_kurs ;;
        4)  run_scrape_utb ;;
        5)  run_vilande ;;
        6)  run_rebuild_mocs ;;
        7)  run_scrape_pipeline ;;
        8)  run_scrape_nedlagda ;;
        9)  run_qa_kurs ;;
        10) run_qa_utb ;;
        11) run_diff ;;
        12) run_populate ;;
        13) run_prune ;;
        14) run_qc_pipeline ;;
        15) run_publish_site ;;
        16) run_serve_site ;;
        q|Q|quit|exit)
            echo "Hejdå."
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Ogiltigt val — ange 1–16 eller q.${RESET}"
            ;;
    esac
    echo ""
done
