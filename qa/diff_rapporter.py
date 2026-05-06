#!/usr/bin/env python3
"""
diff_rapporter.py — Jämför två QA-rapporter och visa vad som lösts / tillkommit.

Användning:
    python3 qa/diff_rapporter.py <gammal-rapport> <ny-rapport>
    python3 qa/diff_rapporter.py --latest2   (välj de två senaste automatiskt)

Utdata (stdout):
    Tre sektioner: LÖSTA (i gammalt men ej i nytt), NYA (i nytt men ej i gammalt),
    KVAR (i båda).
"""
import re
import sys
from pathlib import Path
from collections import defaultdict

# ─────────────────────────────────────────────────────────────────────────────
# Parsning
# ─────────────────────────────────────────────────────────────────────────────
RAPPORT_DIR = Path(__file__).resolve().parent / "rapporter"

# Match table rows: | CODE | SUBJ | DETAIL |
ROW_RE = re.compile(r"^\|\s*([A-ZÅÄÖ0-9][A-Z0-9]{2,8})\s*\|\s*([A-ZÅÄÖ0-9]+)\s*\|(.+)\|?\s*$")
SECTION_RE = re.compile(r"^##\s+(.+?)\s*\(")


def parse_rapport(path: Path) -> list[tuple[str, str, str, str]]:
    """Return list of (section, code, subj, detail) tuples."""
    findings = []
    current_section = "Okänd"
    for line in path.read_text(encoding="utf-8").splitlines():
        m_sec = SECTION_RE.match(line)
        if m_sec:
            current_section = m_sec.group(1).strip()
            continue
        m_row = ROW_RE.match(line)
        if m_row:
            code = m_row.group(1).strip()
            subj = m_row.group(2).strip()
            detail = m_row.group(3).strip().rstrip("|").strip()
            if code.lower() in ("kod", "---"):
                continue
            findings.append((current_section, code, subj, detail))
    return findings


def finding_key(section: str, code: str, detail: str) -> str:
    """Stable identity key for a finding — section + code + first ~60 chars of detail."""
    # Truncate detail so minor whitespace/punctuation changes don't create false positives
    return f"{section}|{code}|{detail[:60]}"


# ─────────────────────────────────────────────────────────────────────────────
# Formatering
# ─────────────────────────────────────────────────────────────────────────────
BOLD  = "\033[1m"
GREEN = "\033[0;32m"
RED   = "\033[0;31m"
YELLOW = "\033[0;33m"
CYAN  = "\033[0;36m"
RESET = "\033[0m"


def print_section(title: str, color: str, rows: list[tuple]):
    if not rows:
        return
    print(f"\n{color}{BOLD}{'─'*60}{RESET}")
    print(f"{color}{BOLD}  {title} ({len(rows)}){RESET}")
    print(f"{color}{BOLD}{'─'*60}{RESET}")
    # Group by section
    by_sec: dict[str, list] = defaultdict(list)
    for section, code, subj, detail in rows:
        by_sec[section].append((code, subj, detail))
    for section, items in sorted(by_sec.items()):
        print(f"\n  {BOLD}{section}{RESET}")
        for code, subj, detail in sorted(items):
            print(f"    {code:<10} {subj:<6}  {detail[:80]}")


# ─────────────────────────────────────────────────────────────────────────────
# Huvud
# ─────────────────────────────────────────────────────────────────────────────
def main():
    args = sys.argv[1:]

    if "--latest2" in args or not args:
        rapporter = sorted(RAPPORT_DIR.glob("rapport-*.md"))
        if len(rapporter) < 2:
            print("Fel: Färre än 2 rapporter hittades i qa/rapporter/.", file=sys.stderr)
            sys.exit(1)
        old_path, new_path = rapporter[-2], rapporter[-1]
    elif len(args) == 2:
        old_path = Path(args[0])
        new_path = Path(args[1])
    else:
        print("Användning: diff_rapporter.py <gammal> <ny>  eller  --latest2", file=sys.stderr)
        sys.exit(1)

    print(f"\n{CYAN}{BOLD}Jämför rapporter{RESET}")
    print(f"  Gammal: {old_path.name}")
    print(f"  Ny:     {new_path.name}")

    old_findings = parse_rapport(old_path)
    new_findings = parse_rapport(new_path)

    old_keys = {finding_key(s, c, d): (s, c, sub, d) for s, c, sub, d in old_findings}
    new_keys = {finding_key(s, c, d): (s, c, sub, d) for s, c, sub, d in new_findings}

    resolved = [v for k, v in old_keys.items() if k not in new_keys]
    new_only  = [v for k, v in new_keys.items() if k not in old_keys]
    unchanged = [v for k, v in old_keys.items() if k in new_keys]

    print_section("LÖSTA — kan tas bort ur analysfilerna", GREEN, resolved)
    print_section("NYA — kräver granskning", RED, new_only)
    print_section("KVAR — ännu ej åtgärdade", YELLOW, unchanged)

    print(f"\n{CYAN}{BOLD}{'─'*60}{RESET}")
    print(f"  {GREEN}{BOLD}Lösta:    {len(resolved):>4}{RESET}  (i gammal, ej i ny)")
    print(f"  {RED}{BOLD}Nya:      {len(new_only):>4}{RESET}  (i ny, ej i gammal)")
    print(f"  {YELLOW}Kvar:     {len(unchanged):>4}{RESET}  (i båda)")
    print()


if __name__ == "__main__":
    main()
