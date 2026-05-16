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
    echo -e "    ${BOLD}6.${RESET}  ${BOLD}Kör alla skrapa-steg${RESET} (2 + 4 + 5)"
    echo ""
    echo -e "  ${MAGENTA}${BOLD}Kvalitetsgranskning${RESET}"
    echo -e "    ${BOLD}7.${RESET}  QA kursplaner (rapport)"
    echo -e "    ${BOLD}8.${RESET}  QA utbildningsplaner (rapport)"
    echo -e "    ${BOLD}9.${RESET}  Jämför kursplan-rapporter (lösta/nya fynd)"
    echo -e "   ${BOLD}10.${RESET}  Populera analysfilerna (från senaste rapport)"
    echo -e "   ${BOLD}11.${RESET}  Rensa analysfilerna (ta bort lösta fynd)"
    echo -e "   ${BOLD}12.${RESET}  ${BOLD}Kör alla QC-steg${RESET} (7 + 8 + 10)"
    echo ""
    echo -e "  ${MAGENTA}${BOLD}Bygg${RESET}"
    echo -e "   ${BOLD}13.${RESET}  Bygg Quartz-sajten (public/)"
    echo -e "   ${BOLD}14.${RESET}  Bygg & förhandsvisa sajten lokalt"
    echo ""
    echo -e "    ${BOLD}q.${RESET}  Avsluta"
    echo ""
}

prompt_apply_mode() {
    # Sätter $APPLY_FLAG till "--apply" eller tom sträng.
    # Hoppas över om $BATCH_APPLY_FLAG redan är satt (för buntade körningar).
    if [[ -n "${BATCH_APPLY_FLAG+x}" ]]; then
        APPLY_FLAG="$BATCH_APPLY_FLAG"
        return
    fi
    local mode
    echo "Läge:"
    echo "  a) Dry-run (visa vad som skulle ändras, skriv ingenting)"
    echo "  b) Apply  (skriv ändringar till disk)"
    echo ""
    read -rp "Välj läge [a/b]: " mode
    case "$mode" in
        b|B) APPLY_FLAG="--apply" ;;
        *)   APPLY_FLAG="" ;;
    esac
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

# ── steg: kör alla skrapa-steg i sekvens ────────────────────────────────────
run_scrape_pipeline() {
    echo -e "${BOLD}Kör alla skrapa-steg${RESET}"
    echo ""
    echo "Kör i sekvens:"
    echo "  • Skrapa ALLA kursplaner (inkl. strö-/orphan-koder)"
    echo "  • Skrapa utbildningsplaner"
    echo "  • Identifiera vilande kursplaner"
    echo ""
    prompt_apply_mode
    BATCH_APPLY_FLAG="$APPLY_FLAG"
    echo ""
    run_scrape_all
    echo ""
    run_scrape_utb
    echo ""
    run_vilande
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
        echo "  Nästa steg: kör menyval 10 för att populera analysfilerna i varje institutions Analys-mapp."
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
    echo -e "${BOLD}Populera analysfilerna${RESET}"
    echo ""
    prompt_apply_mode
    echo ""
    if [[ -n "$APPLY_FLAG" ]]; then
        "$PYTHON" qa/populate_analysfiler.py
    else
        "$PYTHON" qa/populate_analysfiler.py --dry-run
    fi
}

# ── steg: rensa analysfilerna ───────────────────────────────────────────────
run_prune() {
    echo -e "${BOLD}Rensa analysfilerna${RESET}"
    echo ""
    prompt_apply_mode
    echo ""
    if [[ -n "$APPLY_FLAG" ]]; then
        "$PYTHON" qa/prune_analysfiler.py
    else
        "$PYTHON" qa/prune_analysfiler.py --dry-run
    fi
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
        6)  run_scrape_pipeline ;;
        7)  run_qa_kurs ;;
        8)  run_qa_utb ;;
        9)  run_diff ;;
        10) run_populate ;;
        11) run_prune ;;
        12) run_qc_pipeline ;;
        13) run_build_site ;;
        14) run_serve_site ;;
        q|Q|quit|exit)
            echo "Hejdå."
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Ogiltigt val — ange 1–14 eller q.${RESET}"
            ;;
    esac
    echo ""
done
