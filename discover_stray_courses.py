#!/usr/bin/env python3
"""
Discover ALL courses on du.se, including stray/orphaned courses not in subject hierarchies.

Implements multiple discovery strategies to catch every course:
1. Global search API (no subject filter)
2. Course code enumeration (systematic pattern testing)
3. Known code lookups (verify existence)

Output: CSV with all discovered courses and their status.
"""

import argparse
import re
import sys
import time
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup


INSTITUTIONS = {
    "IIT": {"name": "Institutionen för information och teknik", "id": "10206"},
    "IHV": {"name": "Institutionen för hälsa och välfärd", "id": "10207"},
    "IKS": {"name": "Institutionen för kultur och samhälle", "id": "10208"},
    "ISLL": {"name": "Institutionen för språk, litteratur och lärande", "id": "10209"},
}

SEARCH_API = "https://www.du.se/search/Search/Search"
COURSE_PAGE = "https://www.du.se/sv/utbildning/kurser/kurs/?code={code}"
KURSPLAN_PAGE = "https://www.du.se/sv/utbildning/kurser/kursplan/?code={code}"

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "HDa-discovery/1.0"})

REQUEST_DELAY = 0.5  # seconds between requests


def course_exists(code: str) -> bool:
    """
    Check if a course code actually exists on du.se.
    Returns True if kursplan page shows course title.
    """
    try:
        resp = SESSION.get(KURSPLAN_PAGE.format(code=code), timeout=10)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, "html.parser")
            # Check for course title in <h1><span property="name">
            title = soup.find("h1")
            if title and title.find("span", property="name"):
                return True
    except Exception as e:
        print(f"  Error checking {code}: {e}", file=sys.stderr)
    return False


def course_has_active_occasion(code: str) -> bool:
    """
    Check if course has any active occasions (Start vecka).
    Returns True if course page shows upcoming start date.
    """
    try:
        resp = SESSION.get(COURSE_PAGE.format(code=code), timeout=10)
        if resp.status_code == 200:
            return "Start vecka" in resp.text or "startsida" in resp.text.lower()
    except Exception:
        pass
    return False


# ============================================================================
# Discovery Method 1: Global Search (No Subject Filter)
# ============================================================================

def discover_via_global_search(institution_code: str) -> set[str]:
    """
    Search globally within institution with no subject filter.
    Returns set of discovered course codes.
    """
    codes = set()
    institution_id = INSTITUTIONS[institution_code]["id"]
    page = 1
    consecutive_empty = 0

    print(f"\n  [Global Search] Searching {institution_code}...")

    while consecutive_empty < 3:  # Stop after 3 empty pages
        params = {
            "search": "true",
            "q": "",  # Empty query - return all
            "l": "sv",
            "sb": "Relevans",
            "ssv": "1",
            "f": "2",
            "cs": institution_id,  # Filter by institution
            "pi": str(page),
            "et": "2",
        }

        try:
            resp = SESSION.get(SEARCH_API, params=params, timeout=30)
            resp.raise_for_status()
            soup = BeautifulSoup(resp.text, "html.parser")

            # Extract course codes from links
            page_codes = set()
            for a in soup.find_all("a", href=True):
                if "/kurser/kurs/?code=" in a["href"]:
                    match = re.search(r"code=([A-Z]+\d+[A-Z]?)", a["href"])
                    if match:
                        code = match.group(1)
                        page_codes.add(code)
                        codes.add(code)

            if not page_codes:
                consecutive_empty += 1
                print(f"    Page {page}: 0 courses (empty streak: {consecutive_empty}/3)")
            else:
                consecutive_empty = 0
                print(f"    Page {page}: {len(page_codes)} courses (total: {len(codes)})")

            page += 1
            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"    Error on page {page}: {e}", file=sys.stderr)
            break

    print(f"  [Global Search] Found {len(codes)} total courses via global search")
    return codes


# ============================================================================
# Discovery Method 2: Course Code Enumeration
# ============================================================================

COURSE_CODE_PATTERNS = {
    "IIT": [
        # Informatik subjects
        ("GIK", range(200, 400)),  # Grundläggande Informatik
        ("DTA", range(200, 400)),  # Datateknik
        ("MDI", range(200, 400)),  # Mikrodataanalys
        ("ELT", range(200, 400)),  # Elektroteknik
        ("ENT", range(200, 400)),  # Energiteknik
        ("BYT", range(200, 400)),  # Byggteknik
        ("SAM", range(200, 400)),  # Samhällsbyggnadsteknik
        ("MAS", range(200, 400)),  # Maskinteknik
        ("MAT", range(200, 400)),  # Matematik
        ("KEM", range(200, 400)),  # Kemi
        ("FYS", range(200, 400)),  # Fysik
        ("AVT", range(200, 400)),  # Applied math/teknisk
    ],
    "IHV": [
        ("FOY", range(200, 400)),  # Fysiologi / hälsa
        ("OMV", range(200, 400)),  # Omvårdnad
        ("FYT", range(200, 400)),  # Fysiotherapi
        ("MED", range(200, 400)),  # Medicinsk vetenskap
    ],
    "IKS": [
        ("AHI", range(200, 400)),  # Arbetsvetenskap / Hälsa / Historia
        ("KUL", range(200, 400)),  # Kultur
        ("SOC", range(200, 400)),  # Sociologi / Socialt arbete
        ("RÄT", range(200, 400)),  # Rättsvetenskap
        ("EKO", range(200, 400)),  # Ekonomi / Företagsekonomi
    ],
    "ISLL": [
        ("SVE", range(200, 400)),  # Svenska
        ("ENG", range(200, 400)),  # Engelska
        ("SPR", range(200, 400)),  # Språk
        ("LIT", range(200, 400)),  # Litteratur
        ("PED", range(200, 400)),  # Pedagogik
    ],
}


def discover_via_enumeration(institution_code: str) -> set[str]:
    """
    Systematically test course code patterns for existence.
    Returns set of verified course codes.
    """
    codes = set()
    patterns = COURSE_CODE_PATTERNS.get(institution_code, [])

    print(f"\n  [Enumeration] Testing course code patterns for {institution_code}...")

    total_tests = 0
    for prefix, number_ranges in patterns:
        print(f"    Testing {prefix}*** pattern...")
        for number in number_ranges:
            code = f"{prefix}{number}"
            total_tests += 1

            if course_exists(code):
                codes.add(code)
                print(f"      ✓ {code} exists", file=sys.stdout)

            if total_tests % 50 == 0:
                time.sleep(REQUEST_DELAY * 5)  # Rate limiting every 50
            else:
                time.sleep(REQUEST_DELAY)

    print(f"  [Enumeration] Verified {len(codes)} courses via enumeration")
    return codes


# ============================================================================
# Discovery Method 3: Check Known Stray Courses
# ============================================================================

def discover_known_stray(institution_code: str) -> set[str]:
    """
    Test specific known/suspected stray courses for existence.
    """
    candidates = [
        # Known examples
        "GIK289",  # Objektorienterad programmering
    ]

    codes = set()
    print(f"\n  [Known Stray] Checking {len(candidates)} suspected codes...")

    for code in candidates:
        if course_exists(code):
            codes.add(code)
            print(f"    ✓ {code} exists")
            time.sleep(REQUEST_DELAY)
        else:
            print(f"    ✗ {code} not found")

    return codes


# ============================================================================
# Main Discovery Orchestration
# ============================================================================

def discover_all_courses(
    institution_code: str,
    methods: list[str] = None,
) -> dict[str, dict]:
    """
    Orchestrate all discovery methods and return comprehensive course inventory.
    Returns: {code: {"aktiv": bool, "name": str, "methods": [list of discovery methods]}}
    """
    if methods is None:
        methods = ["global", "enumeration", "known"]

    all_discovered = {}

    # Run each method
    if "global" in methods:
        global_courses = discover_via_global_search(institution_code)
        for code in global_courses:
            if code not in all_discovered:
                all_discovered[code] = {
                    "methods": [],
                    "aktiv": False,
                    "name": "",
                }
            all_discovered[code]["methods"].append("global")

    if "enumeration" in methods:
        enum_courses = discover_via_enumeration(institution_code)
        for code in enum_courses:
            if code not in all_discovered:
                all_discovered[code] = {
                    "methods": [],
                    "aktiv": False,
                    "name": "",
                }
            all_discovered[code]["methods"].append("enumeration")

    if "known" in methods:
        known_courses = discover_known_stray(institution_code)
        for code in known_courses:
            if code not in all_discovered:
                all_discovered[code] = {
                    "methods": [],
                    "aktiv": False,
                    "name": "",
                }
            all_discovered[code]["methods"].append("known")

    # Verify active status for all discovered courses
    print(f"\n  [Verification] Checking active occasions for {len(all_discovered)} courses...")
    verified_count = 0
    for code, info in all_discovered.items():
        info["aktiv"] = course_has_active_occasion(code)
        verified_count += 1
        if verified_count % 20 == 0:
            print(f"    Verified {verified_count}/{len(all_discovered)}")
        time.sleep(REQUEST_DELAY / 2)

    return all_discovered


# ============================================================================
# Output
# ============================================================================

def print_results(courses: dict[str, dict], institution_code: str):
    """Print discovered courses in readable format."""
    aktiv = [c for c, info in courses.items() if info["aktiv"]]
    vilande = [c for c, info in courses.items() if not info["aktiv"]]

    print(f"\n{'='*70}")
    print(f"DISCOVERY SUMMARY: {institution_code}")
    print(f"{'='*70}")
    print(f"Total discovered: {len(courses)}")
    print(f"  - Aktiv (with occasions): {len(aktiv)}")
    print(f"  - Vilande (no occasions): {len(vilande)}")

    if vilande:
        print(f"\nVilande courses ({len(vilande)}):")
        for code in sorted(vilande):
            methods = courses[code]["methods"]
            print(f"  {code:10} (found via: {', '.join(methods)})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Discover all courses on du.se")
    parser.add_argument(
        "institution",
        nargs="?",
        choices=list(INSTITUTIONS.keys()),
        help="Institution to search (IIT, IHV, IKS, ISLL)",
    )
    parser.add_argument(
        "--method",
        nargs="+",
        default=["global"],
        choices=["global", "enumeration", "known"],
        help="Discovery methods to use",
    )
    parser.add_argument(
        "--all",
        action="store_true",
        help="Run all methods (default is global only)",
    )

    args = parser.parse_args()

    if not args.institution:
        print("Usage: python3 discover_stray_courses.py IIT|IHV|IKS|ISLL")
        sys.exit(1)

    methods = ["global", "enumeration", "known"] if args.all else args.method

    try:
        courses = discover_all_courses(args.institution, methods=methods)
        print_results(courses, args.institution)
    except KeyboardInterrupt:
        print("\nInterrupted by user", file=sys.stderr)
        sys.exit(1)
