"""
Kvalitetskontroller som drar nytta av QA-cachen i ``qa/nedlagda-kursplaner/``.

Cachen byggs av ``scripts/scrape_hda_nedlagda.py`` (menyval 7 i ``hda.sh``)
och innehåller en slim metadatafil per nedlagd kursplan på du.se. Den används
för:

  * att flagga utbildningsplaner som listar kurser som idag är nedlagda
    (kursen finns inte längre som aktiv kursplan på du.se men programmet
    refererar fortfarande till den — vanligaste fyndet är kurser i plain-
    text-form, alltså utan ``[[…]]``/``no-graph``-länk eftersom skrapan
    inte hittade någon aktiv kandidat)
  * att skilja "kursplan finns kvar men kursomgång saknas" (vilande) från
    "kursplan officiellt nedlagd" i kvalitetsanalysen av kurssatset
  * (kommande) som auktoritativ källa när förkunskapskrav nämner en kurs
    som vi inte kan matcha mot aktiv katalog

Modulen läser bara cachen — den hämtar inget från du.se.
"""

from __future__ import annotations

import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
NEDLAGDA_DIR = REPO_ROOT / "qa" / "nedlagda-kursplaner"
VAULT = REPO_ROOT / "vault-dalarna-university"
INST_DIRS = ["01 IIT", "02 IHV", "03 IKS", "04 ISLL"]


# Aggressiv namnnormalisering — speglar matcharen i
# ``scripts/scrape_hda_utbildningsplaner.py``. Vi duplicerar den medvetet
# här för att hålla qa/-modulerna oberoende av scripts/.
_AKK_RE = re.compile(r"\b(?:åk|årskurs)\s+(?=[F\d])", re.I)
_DASH_WS_RE = re.compile(r"\s*[-–—]\s*")
_MULTI_WS_RE = re.compile(r"\s+")


def _aggressive(name: str) -> str:
    n = name.strip().lower()
    n = _AKK_RE.sub("", n)
    n = _DASH_WS_RE.sub("-", n)
    n = _MULTI_WS_RE.sub(" ", n)
    return n.strip()


# ─────────────────────────────────────────────────────────────────────────────
# Cache-läsare
# ─────────────────────────────────────────────────────────────────────────────

class NedlagdaIndex:
    """In-memory-uppslagning över ``qa/nedlagda-kursplaner/``.

    ``by_code`` mappar kurskod → metadata-dict (kursnamn, ämne, institution,
    nedlagd-datum). ``by_name`` mappar normaliserat kursnamn → kurskod. Vid
    namnkollision (samma kursnamn på flera koder) lagras den senast nedlagda
    kursen — det är den variant utbildningsplaner mest sannolikt refererar
    till.
    """

    def __init__(self, by_code: dict[str, dict], by_name: dict[str, str]) -> None:
        self.by_code = by_code
        self.by_name = by_name

    def lookup_code(self, code: str) -> dict | None:
        return self.by_code.get(code.upper())

    def lookup_name(self, name: str) -> dict | None:
        agg = _aggressive(name)
        code = self.by_name.get(agg)
        if not code:
            # Sista utväg — kolla mot kolon-prefix (programmets bullets bär
            # ibland en undertitel som kursplanens namn saknar).
            if ":" in name:
                prefix = name.split(":", 1)[0].strip()
                code = self.by_name.get(_aggressive(prefix))
        if code:
            return self.by_code.get(code)
        return None

    def __len__(self) -> int:
        return len(self.by_code)


_INDEX_CACHE: NedlagdaIndex | None = None
_ACTIVE_TITLES: set[str] | None = None


def _load_active_titles() -> set[str]:
    """Aggressivt-normaliserade kursnamn från alla nuvarande vault-kursplaner.

    Används för att filtrera bort falska positiva i nedlagda-checken: om en
    förkunskapsfras matchar både en aktiv vault-kurs och en nedlagd
    kursplan-kod, är det den aktiva som åsyftas. Vi behandlar därför "har
    aktiv träff" som överordnat.
    """
    global _ACTIVE_TITLES
    if _ACTIVE_TITLES is not None:
        return _ACTIVE_TITLES
    titles: set[str] = set()
    name_re = re.compile(r'^kursnamn:\s*"?([^"\n]+?)"?\s*$', re.M)
    for inst in INST_DIRS:
        kp = VAULT / inst / "Kursplaner"
        if not kp.exists():
            continue
        for path in kp.rglob("*.md"):
            if "MOC" in path.name:
                continue
            try:
                head = path.read_text(encoding="utf-8")[:1500]
            except OSError:
                continue
            if not head.startswith("---"):
                continue
            end = head.find("\n---", 3)
            if end < 0:
                continue
            m = name_re.search(head[3:end])
            if m:
                titles.add(_aggressive(m.group(1)))
    _ACTIVE_TITLES = titles
    return titles


def load_index(refresh: bool = False) -> NedlagdaIndex:
    """Bygg (eller hämta cachad) uppslagning över nedlagda kursplaner.

    Tar ~50ms över 6500 filer; ändå värt att cacha eftersom flera checks
    delar samma index i samma körning.
    """
    global _INDEX_CACHE
    if _INDEX_CACHE is not None and not refresh:
        return _INDEX_CACHE

    by_code: dict[str, dict] = {}
    by_name: dict[str, str] = {}

    if not NEDLAGDA_DIR.exists():
        _INDEX_CACHE = NedlagdaIndex({}, {})
        return _INDEX_CACHE

    field_re = re.compile(r'^([a-zåäö_]+):\s*"?([^"\n]*?)"?\s*$', re.M)
    for path in NEDLAGDA_DIR.glob("*.md"):
        code = path.stem
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        # Frontmatter slutar vid andra ``---``.
        if not text.startswith("---"):
            continue
        end = text.find("\n---", 3)
        if end < 0:
            continue
        fm = text[3:end]
        meta: dict[str, str] = {}
        for m in field_re.finditer(fm):
            meta[m.group(1)] = m.group(2).strip()
        name = meta.get("kursnamn", "")
        if not name:
            continue
        record = {
            "code": code,
            "kursnamn": name,
            "amne": meta.get("amne", ""),
            "amneskod": meta.get("amneskod", ""),
            "institution": meta.get("institution", ""),
            "nedlagd": meta.get("nedlagd", ""),
        }
        by_code[code] = record
        agg = _aggressive(name)
        # Konfliktlösning: behåll posten med senast nedlagd-datum (lexikalisk
        # YYYY-MM-DD sortering räcker).
        prev = by_name.get(agg)
        if prev is None or record["nedlagd"] > by_code[prev].get("nedlagd", ""):
            by_name[agg] = code

    _INDEX_CACHE = NedlagdaIndex(by_code, by_name)
    return _INDEX_CACHE


# ─────────────────────────────────────────────────────────────────────────────
# Bullet-parser för utbildningsplaner
# ─────────────────────────────────────────────────────────────────────────────

# Section 3-bullets renderas i tre former (se scrape_hda_utbildningsplaner.py):
#   1. ``- [[CODE|namn]], hp``   (aktiv kursplan, samma institution)
#   2. ``- <a class="no-graph" href="CODE">namn</a>, hp``  (aktiv, korsinst.)
#   3. ``- Namn, hp``             (oklassad — kan vara nedlagd)
_BULLET_WIKILINK = re.compile(
    r'^\s*-\s*\[\[([A-Z0-9]+)\|([^\]]+)\]\]\s*,\s*([\d.,]+\s*hp)',
    re.I,
)
_BULLET_NOGRAPH = re.compile(
    r'^\s*-\s*<a class="no-graph" href="([A-Z0-9]+)">([^<]+)</a>\s*,\s*([\d.,]+\s*hp)',
    re.I,
)
# Plain-text bullet kräver ``, N hp`` i slutet och avvisar wikilink/anchor.
_BULLET_PLAIN = re.compile(
    r'^\s*-\s*(?![\[<])(.+?)\s*,\s*(\d+(?:[,.]\d+)?\s*hp)\s*$',
    re.I,
)


def _course_section(text: str) -> str:
    """Returnera section 3 (``## 3. Programmets kurser``) eller tomt."""
    m = re.search(
        r"^## 3\.[^\n]*\n(.+?)(?=^## \d|\Z)",
        text, re.M | re.S,
    )
    return m.group(1) if m else ""


def scan_programme_bullets(text: str) -> list[dict]:
    """Plocka ut alla kursbullets ur sektion 3.

    Varje träff returneras som ``{"form": "wikilink"|"nograph"|"plain",
    "code": str|None, "name": str, "hp": str, "line": str}``.
    """
    sec = _course_section(text)
    if not sec:
        return []
    out: list[dict] = []
    for raw in sec.split("\n"):
        line = raw.rstrip()
        m = _BULLET_WIKILINK.match(line)
        if m:
            out.append({"form": "wikilink", "code": m.group(1).upper(),
                        "name": m.group(2).strip(), "hp": m.group(3),
                        "line": line.strip()})
            continue
        m = _BULLET_NOGRAPH.match(line)
        if m:
            out.append({"form": "nograph", "code": m.group(1).upper(),
                        "name": m.group(2).strip(), "hp": m.group(3),
                        "line": line.strip()})
            continue
        m = _BULLET_PLAIN.match(line)
        if m:
            out.append({"form": "plain", "code": None,
                        "name": m.group(1).strip(), "hp": m.group(2),
                        "line": line.strip()})
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Check — nedlagda referenser i utbildningsplaner
# ─────────────────────────────────────────────────────────────────────────────

def check_nedlagda_refs_utb(files: list[Path]) -> list[dict]:
    """Flaggar utbildningsplaner som listar nedlagda kurser.

    Tre fall:

    * **Plain-text bullet matchar nedlagd kursplan**: programmet refererar
      till en kurs som inte längre erbjuds (vanligaste fyndet — TPOKG-fallet
      med "Statistik för ingenjörer", "Tillverkningsteknik" m.fl.).
    * **Wikilink eller no-graph-anchor pekar på nedlagd kurskod**: ovanligt
      men fångar fall där aktiv-indexet och du.se kommit ur synk.
    * **Plain-text bullet utan motsvarighet** i nedlagda-cachen rapporteras
      inte här — det är ett annat slags problem (kurs som aldrig fanns på
      du.se, stavfel, alternativkurs etc.).
    """
    index = load_index()
    if len(index) == 0:
        return []
    active_titles = _load_active_titles()

    findings: list[dict] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        prog_code = path.stem
        for bullet in scan_programme_bullets(text):
            hit: dict | None = None
            reason = ""
            if bullet["form"] == "plain":
                # Hoppa över om kursnamnet också finns aktivt — då åsyftar
                # programmet sannolikt den aktiva kursen och plain-text-
                # raden är bara en matchningsmiss i scrapern.
                if _aggressive(bullet["name"]) in active_titles:
                    continue
                hit = index.lookup_name(bullet["name"])
                if hit:
                    reason = "plain-text-referens"
            elif bullet["code"]:
                hit = index.lookup_code(bullet["code"])
                if hit:
                    reason = f"{bullet['form']}-länk till nedlagd kod"
            if not hit:
                continue
            ned_date = hit["nedlagd"] or "okänt datum"
            detail = (
                f"`{bullet['name']}` → `{hit['code']}` "
                f"(nedlagd {ned_date}) — {reason}; "
                f"rad: {bullet['line']}"
            )
            findings.append({
                "check": "nedlagd-kursreferens",
                "code": prog_code,
                "subj": path.parent.name,
                "detail": detail,
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check — nedlagda referenser i kursplaners förkunskapskrav
# ─────────────────────────────────────────────────────────────────────────────

_PREREQ_SECTION_RE = re.compile(
    r"^## Förkunskapskrav\s*\n(.+?)(?=^## |\Z)",
    re.M | re.S,
)

# Hittar varje förekomst av ``N hp`` i en text. Vi använder positionen som
# ankarpunkt och kandidatextraherar de 2–6 ord som föregår — det är där
# kursnamnet faktiskt står.
_HP_TOKEN_RE = re.compile(r"\b(\d+(?:[,.]\d+)?)\s*hp\b", re.I)

# Brytpunkter som signalerar att kursnamnet börjar efter detta.
_CANDIDATE_BREAK = re.compile(
    r"\b(?:inklusive|kursen|kurserna|samt|och)\s+|[,;:]\s+|^\s*-\s+",
    re.I | re.M,
)


def _candidate_phrases(prereq_text: str, hp_pos: int) -> list[str]:
    """Returnera möjliga kursnamn omedelbart före ``hp_pos`` i texten.

    Vi tar de senaste 120 tecknen, klyver vid kända brytpunkter ("kursen X",
    "inklusive Y", "och Z, …") och returnerar varje resulterande slut-fras
    som en kandidat. Längsta först så att specifika namn vinner över generiska.
    """
    start = max(0, hp_pos - 120)
    chunk = prereq_text[start:hp_pos].rstrip(" ,;:")
    pieces = _CANDIDATE_BREAK.split(chunk)
    candidates: list[str] = []
    for piece in pieces:
        cand = piece.strip(" ,;:.")
        if not cand or len(cand) < 4:
            continue
        # Kursnamn börjar i regel med versal eller en siffra (t.ex. "3D CAD …").
        if not (cand[0].isupper() or cand[0].isdigit()):
            continue
        candidates.append(cand)
    # Längsta kandidaten är mest specifik — pröva den först.
    candidates.sort(key=len, reverse=True)
    return candidates


def check_nedlagda_prereqs_kurs(files: list[Path]) -> list[dict]:
    """Flaggar kursplaner vars ``## Förkunskapskrav`` nämner nedlagd kurs.

    Förkunskapskrav är fri prosa — vi extraherar varje ``N hp``-token och
    försöker matcha de föregående 2–6 orden mot nedlagda-cachens namnindex.
    En träff betyder att kursplanen kräver en kurs som inte längre erbjuds
    — antingen behöver kravet skrivas om eller så är referensen kvar i
    kursplanen av historiska skäl och bör städas.

    Sannolika falska positiva: "180 hp och Engelska 6" e.dyl. examenskrav
    matchar inget i nedlagda-cachen och filtreras därför bort i praktiken.
    """
    index = load_index()
    if len(index) == 0:
        return []
    active_titles = _load_active_titles()

    findings: list[dict] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        m = _PREREQ_SECTION_RE.search(text)
        if not m:
            continue
        prereq = m.group(1)
        seen_codes: set[str] = set()
        for hp_m in _HP_TOKEN_RE.finditer(prereq):
            for cand in _candidate_phrases(prereq, hp_m.start()):
                # En aktiv vault-kurs med samma namn vinner — då är det
                # den aktiva versionen som åsyftas.
                if _aggressive(cand) in active_titles:
                    break
                hit = index.lookup_name(cand)
                if not hit or hit["code"] in seen_codes:
                    continue
                seen_codes.add(hit["code"])
                ned_date = hit["nedlagd"] or "okänt datum"
                findings.append({
                    "check": "nedlagd-förkunskapskrav",
                    "code": path.stem,
                    "subj": path.parent.name,
                    "detail": (
                        f"`{cand}` → `{hit['code']}` "
                        f"(nedlagd {ned_date}); förkunskap nämner nedlagd kurs"
                    ),
                })
                break
    return findings
