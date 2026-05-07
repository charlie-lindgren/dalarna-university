#!/usr/bin/env bash
# hda.sh — Meny för Högskolan Dalarna kvalitetsarbetsflöde
# Kör från repo-roten: ./hda.sh

set -euo pipefail
cd "$(dirname "$0")"

PYTHON="${PYTHON:-python3}"
RAPPORT_DIR="qa/rapporter"
RAPPORT_DIR_UTB="qa/rapporter-utb"

# ── färger ──────────────────────────────────────────────────────────────────
BOLD='\033[1m'
CYAN='\033[0;36m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RESET='\033[0m'

print_header() {
    echo ""
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo -e "${CYAN}${BOLD}  Högskolan Dalarna — Plananalys${RESET}"
    echo -e "${CYAN}${BOLD}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${RESET}"
    echo ""
}

print_menu() {
    echo -e "  ${BOLD}1.${RESET}  Skrapa kursplaner från du.se"
    echo -e "  ${BOLD}2.${RESET}  Skrapa utbildningsplaner från du.se"
    echo -e "  ${BOLD}3.${RESET}  QA kursplaner (rapport)"
    echo -e "  ${BOLD}4.${RESET}  QA utbildningsplaner (rapport)"
    echo -e "  ${BOLD}5.${RESET}  Jämför kursplan-rapporter (lösta/nya fynd)"
    echo -e "  ${BOLD}6.${RESET}  Rensa analysfilerna (ta bort lösta fynd)"
    echo -e "  ${BOLD}7.${RESET}  Populera analysfilerna (från senaste rapport)"
    echo -e "  ${BOLD}8.${RESET}  Identifiera ej-aktiva kursplaner (orphan-detektor)"
    echo -e "  ${BOLD}q.${RESET}  Avsluta"
    echo ""
}

# ── steg: skrapning kursplaner ──────────────────────────────────────────────
run_scrape_kurs() {
    echo -e "${BOLD}Skrapa kursplaner${RESET}"
    echo ""
    echo "Läge:"
    echo "  a) Dry-run (visa vad som skulle ändras, skriv ingenting)"
    echo "  b) Apply  (skriv ändringar till vault)"
    echo ""
    read -rp "Välj läge [a/b]: " mode
    case "$mode" in
        b|B)
            echo -e "${YELLOW}Kör scrape --apply …${RESET}"
            "$PYTHON" scrape_hda_kursplaner.py --apply
            ;;
        *)
            echo -e "${YELLOW}Kör scrape dry-run …${RESET}"
            "$PYTHON" scrape_hda_kursplaner.py
            ;;
    esac
    echo -e "${GREEN}✓ Kursplan-skrapning klar${RESET}"
}

# ── steg: skrapning utbildningsplaner ───────────────────────────────────────
run_scrape_utb() {
    echo -e "${BOLD}Skrapa utbildningsplaner${RESET}"
    echo ""
    echo "Läge:"
    echo "  a) Dry-run"
    echo "  b) Apply"
    echo ""
    read -rp "Välj läge [a/b]: " mode
    case "$mode" in
        b|B)
            echo -e "${YELLOW}Kör scrape --apply …${RESET}"
            "$PYTHON" scrape_hda_utbildningsplaner.py --apply
            ;;
        *)
            echo -e "${YELLOW}Kör scrape dry-run …${RESET}"
            "$PYTHON" scrape_hda_utbildningsplaner.py
            ;;
    esac
    echo -e "${GREEN}✓ Utbildningsplan-skrapning klar${RESET}"
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
    "$PYTHON" qa/check_kursplaner.py $SKIP_HUNSPELL --out "$OUTFILE"

    echo ""
    echo -e "${GREEN}✓ QA-rapport sparad: ${BOLD}${OUTFILE}${RESET}"
    echo ""
    echo "  Nästa steg: kör menyval 7 för att populera analysfilerna i 03 Analys/."
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

# ── steg: rensa analysfilerna ───────────────────────────────────────────────
run_prune() {
    echo -e "${BOLD}Rensa analysfilerna${RESET}"
    echo ""
    echo "Läge:"
    echo "  a) Dry-run"
    echo "  b) Apply"
    echo ""
    read -rp "Välj läge [a/b]: " mode
    echo ""
    case "$mode" in
        b|B) "$PYTHON" qa/prune_analysfiler.py ;;
        *)   "$PYTHON" qa/prune_analysfiler.py --dry-run ;;
    esac
}

# ── steg: populera analysfilerna ────────────────────────────────────────────
run_populate() {
    echo -e "${BOLD}Populera analysfilerna${RESET}"
    echo ""
    echo "Läge:"
    echo "  a) Dry-run"
    echo "  b) Apply"
    echo ""
    read -rp "Välj läge [a/b]: " mode
    echo ""
    case "$mode" in
        b|B) "$PYTHON" qa/populate_analysfiler.py ;;
        *)   "$PYTHON" qa/populate_analysfiler.py --dry-run ;;
    esac
}


# ── steg: identifiera ej-aktiva kursplaner ──────────────────────────────────
run_ej_aktiv() {
    echo -e "${BOLD}Identifiera ej-aktiva kursplaner${RESET}"
    echo ""
    echo "Hämtar nuvarande kurslistor från du.se och jämför mot vault."
    echo "Tar några minuter."
    echo ""
    echo "Läge:"
    echo "  a) Dry-run"
    echo "  b) Apply"
    echo ""
    read -rp "Välj läge [a/b]: " mode
    echo ""
    case "$mode" in
        b|B) "$PYTHON" qa/identify_ej_aktiv.py --apply ;;
        *)   "$PYTHON" qa/identify_ej_aktiv.py ;;
    esac
}


print_header
while true; do
    print_menu
    read -rp "Val: " choice
    echo ""
    case "$choice" in
        1) run_scrape_kurs ;;
        2) run_scrape_utb ;;
        3) run_qa_kurs ;;
        4) run_qa_utb ;;
        5) run_diff ;;
        6) run_prune ;;
        7) run_populate ;;
        8) run_ej_aktiv ;;
        q|Q|quit|exit)
            echo "Hejdå."
            exit 0
            ;;
        *)
            echo -e "${YELLOW}Ogiltigt val — ange 1–8 eller q.${RESET}"
            ;;
    esac
    echo ""
done
