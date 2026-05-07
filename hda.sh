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
    echo -e "  ${MAGENTA}${BOLD}Skrapa & bygg${RESET}"
    echo -e "    ${BOLD}1.${RESET}  ${BOLD}Skrapa ALLA kursplaner${RESET} (inkl. strö-/orphan-koder)"
    echo -e "    ${BOLD}2.${RESET}  Skrapa kursplaner (endast ordinarie ämnen)"
    echo -e "    ${BOLD}3.${RESET}  Skrapa utbildningsplaner"
    echo -e "    ${BOLD}4.${RESET}  Identifiera vilande kursplaner"
    echo -e "    ${BOLD}5.${RESET}  Bygg Quartz-sajten (public/)"
    echo -e "    ${BOLD}6.${RESET}  Bygg & förhandsvisa sajten lokalt"
    echo ""
    echo -e "  ${MAGENTA}${BOLD}Kvalitetsgranskning${RESET}"
    echo -e "    ${BOLD}7.${RESET}  QA kursplaner (rapport)"
    echo -e "    ${BOLD}8.${RESET}  QA utbildningsplaner (rapport)"
    echo -e "    ${BOLD}9.${RESET}  Jämför kursplan-rapporter (lösta/nya fynd)"
    echo -e "   ${BOLD}10.${RESET}  Populera analysfilerna (från senaste rapport)"
    echo -e "   ${BOLD}11.${RESET}  Rensa analysfilerna (ta bort lösta fynd)"
    echo ""
    echo -e "    ${BOLD}q.${RESET}  Avsluta"
    echo ""
}

prompt_apply_mode() {
    # Sätter $APPLY_FLAG till "--apply" eller tom sträng.
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
    echo "Detta tar fram alla kursplaner som finns på du.se, inklusive"
    echo "strö-/orphan-koder som inte syns i ämnes- eller programlistan."
    echo "Strökoder upptäcks i två steg:"
    echo "  1. Kanonisk sökning på du.se (~50 paginerade anrop, ~1 min)."
    echo "  2. Valfri lucka-probing av kodserier när padding > 0 (parallell)."
    echo ""
    echo -e "${YELLOW}Default (padding=0) är snabbt; padding > 0 lägger till djupare probing.${RESET}"
    echo ""

    prompt_apply_mode

    local padding
    read -rp "Strö-padding (utöka spann med N nummer i båda ändar) [0]: " padding
    padding="${padding:-0}"

    echo ""
    echo -e "${YELLOW}Kör scrape --discover-stray ${APPLY_FLAG} …${RESET}"
    # shellcheck disable=SC2086
    "$PYTHON" scrape_hda_kursplaner.py \
        --discover-stray \
        --stray-padding "$padding" \
        $APPLY_FLAG

    echo ""
    echo -e "${GREEN}✓ Fullständig kursplan-skrapning klar${RESET}"
    if [[ -n "$APPLY_FLAG" ]]; then
        echo "  Tips: kör menyval 4 för att tagga vilande kursplaner."
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
    "$PYTHON" scrape_hda_kursplaner.py $APPLY_FLAG
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
    "$PYTHON" scrape_hda_utbildningsplaner.py $APPLY_FLAG
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
    echo ""
    echo "  Nästa steg: kör menyval 10 för att populera analysfilerna i varje institutions Analys-mapp."
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

print_header
while true; do
    print_menu
    read -rp "Val: " choice
    echo ""
    case "$choice" in
        1)  run_scrape_all ;;
        2)  run_scrape_kurs ;;
        3)  run_scrape_utb ;;
        4)  run_vilande ;;
        5)  run_build_site ;;
        6)  run_serve_site ;;
        7)  run_qa_kurs ;;
        8)  run_qa_utb ;;
        9)  run_diff ;;
        10) run_populate ;;
        11) run_prune ;;
        q|Q|quit|exit)
            echo "Hejdå."
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Ogiltigt val — ange 1–11 eller q.${RESET}"
            ;;
    esac
    echo ""
done
