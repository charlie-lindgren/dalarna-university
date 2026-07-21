"""
Kvalitetskontroller som drar nytta av QA-cachen i ``qa/nedlagda-kursplaner/``.

Cachen byggs av ``scripts/scrape_hda_nedlagda.py`` (menyval 8 i ``hda.sh``)
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

# Nedlagda kursplaner ligger kvar i vaulten men bär ``draft: true`` (satt av
# identify_ej_aktiv.py). De "aktiva" indexen nedan ska bara innehålla levande
# kurser — annars maskerar en nedlagd kurs sig som aktiv och en genuin
# nedlagd-referens filtreras felaktigt bort som falsk positiv.
_DRAFT_LINE_RE = re.compile(r"^draft:\s*true\s*$", re.MULTILINE)


# Aggressiv namnnormalisering — speglar matcharen i
# ``scripts/scrape_hda_utbildningsplaner.py``. Vi duplicerar den medvetet
# här för att hålla qa/-modulerna oberoende av scripts/.
# Programkurslistor i utbildningsplaner (företrädelsevis från IHV/Omvårdnad)
# bär ibland en huvudområdes-stämpel i slutet av kursnamnet:
#   ``Människa, hälsa och samhälle - Huvudområde Omvårdnad, 7,5 hp``
# Stämpeln är ren administrativ metadata — själva kursplanens ``kursnamn:`` är
# ``Människa, hälsa och samhälle``. Strip suffixet vid normalisering så att
# matchningen mot aktivt kursindex lyckas och bullets länkas i stället för att
# rapporteras som okända.
_HUVUDOMRADE_SUFFIX_RE = re.compile(r"\s+-\s+huvudområde\b.*$")
# Lärarprogrammens AIL-varianter ("arbetsintegrerat lärande") får ett
# ``- AIL``-suffix i programtexten medan kursplanen själv inte bär det.
# Strip suffixet vid normalisering så bulleten länkas mot rätt kurskod.
_AIL_SUFFIX_RE = re.compile(r"\s+[-–—]\s+ail\s*$")
# Soft hyphen (U+00AD) sprids in via HTML-export — osynligt tecken som inte
# bör hindra matchning.
_SOFT_HYPHEN_RE = re.compile(r"­")
_AKK_RE = re.compile(r"\b(?:åk|årskurs)\s+(?=[F\d])", re.I)
# Svensk ellips i sammansättningar: "System- och verksamhetsutveckling" är
# en kortform av "Systemutveckling och verksamhetsutveckling". För matchning
# ska den vara likvärdig med "System och verksamhetsutveckling" — annars
# blir nedlagda GIK2JW felaktigt prioriterad framför aktiva GIK2XZ.
_ELLIPSIS_DASH_RE = re.compile(r"(?<=\w)[-–—](?=\s)")
_DASH_WS_RE = re.compile(r"\s*[-–—]\s*")
# Slash i kurskursnamn ("CAM/CNC", "CAD/CAM") skrivs ibland med mellanslag i
# utbildningsplaner ("CAM / CNC") — kollapsa whitespace runt slash så att
# bägge former hashas till samma nyckel.
_SLASH_WS_RE = re.compile(r"\s*/\s*")
_MULTI_WS_RE = re.compile(r"\s+")
# Kursnivåer skrivs omväxlande med romerska och arabiska siffror — "Audioteknologi
# I" i utbildningsplanen mot "Audioteknologi 1" i kursplanen, "Datakommunikation
# I" mot "Datakommunikation 1". Ett *ensamt* romerskt tal sist i namnet (eller
# sist före en kolon-underrubrik) normaliseras till arabisk siffra så att
# formerna hashas lika. Begränsat till I–VI: bokstaven "i" är också svensk
# preposition, så mönstret kräver ordgräns *och* radslut/kolon för att inte
# träffa "Kommunikation i samhället".
_ROMAN_TAIL_RE = re.compile(r"\b(?<![-/])(i{1,3}|iv|vi?)(?=\s*(?::|$))")
_ROMAN_TO_ARABIC = {"i": "1", "ii": "2", "iii": "3", "iv": "4", "v": "5", "vi": "6"}
# Utbildningsplanernas kurslistor bär ibland ett hängande skiljetecken från
# du.se-exporten — LLL6A skriver "… åk 4–6,, 15 hp", vilket ger kursnamnet ett
# efterföljande kommatecken. Strippas före jämförelse.
_TRAILING_PUNCT_RE = re.compile(r"[\s,;.:–—-]+$")


def _aggressive(name: str) -> str:
    n = name.strip().lower()
    n = _SOFT_HYPHEN_RE.sub("", n)
    n = _HUVUDOMRADE_SUFFIX_RE.sub("", n)
    n = _AIL_SUFFIX_RE.sub("", n)
    n = _AKK_RE.sub("", n)
    n = _ELLIPSIS_DASH_RE.sub("", n)
    n = _DASH_WS_RE.sub("-", n)
    n = _SLASH_WS_RE.sub("/", n)
    n = _MULTI_WS_RE.sub(" ", n)
    n = _TRAILING_PUNCT_RE.sub("", n)
    n = _ROMAN_TAIL_RE.sub(lambda m: _ROMAN_TO_ARABIC[m.group(1)], n)
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

    ``by_suffix`` speglar ``by_name`` men med kursplanens ämnes-prefix
    avskalat: arkivet skriver ``Afrikanska studier: Södra Afrikas moderna
    historia`` medan HAFSA:s kurslista bara skriver ``Södra Afrikas moderna
    historia``. Samma kortform som ``_normalize_for_display_compare`` redan
    accepterar för aktiva kurser.
    """

    def __init__(self, by_code: dict[str, dict], by_name: dict[str, str]) -> None:
        self.by_code = by_code
        self.by_name = by_name
        self.by_suffix: dict[str, str] = {}
        for agg_name, code in by_name.items():
            m = _SUBJECT_PREFIX_RE.match(agg_name)
            if not m:
                continue
            suffix = agg_name[m.end():].strip()
            # Bara entydiga suffix duger — bär två ämnen samma kursnamn
            # (``Franska: Examensarbete`` vs ``Italienska: Examensarbete``) går
            # det inte att avgöra vilket som åsyftas, så nyckeln tas bort.
            if suffix and suffix not in self.by_name:
                self.by_suffix[suffix] = "" if suffix in self.by_suffix else code
        self.by_suffix = {k: v for k, v in self.by_suffix.items() if v}

    def lookup_code(self, code: str) -> dict | None:
        return self.by_code.get(code.upper())

    def lookup_name(self, name: str) -> dict | None:
        agg = _aggressive(name)
        code = self.by_name.get(agg)
        if not code:
            # Programtexten utelämnar ofta kursplanens ämnes-prefix.
            code = self.by_suffix.get(agg)
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
_ACTIVE_CODE_TO_NAME: dict[str, str] | None = None
_VILANDE_CODES: set[str] | None = None

_VILANDE_FM_RE = re.compile(r"^(?:tags|cssclasses):.*\bvilande\b", re.M)


def _load_vilande_codes() -> set[str]:
    """Kurskoder vars kursplan är taggad ``vilande`` (kursen ges inte just nu).

    Används för att välja rätt kod när flera kursplaner delar samma kursnamn —
    en aktiv kod är alltid ett bättre förslag än en vilande."""
    global _VILANDE_CODES
    if _VILANDE_CODES is not None:
        return _VILANDE_CODES
    codes: set[str] = set()
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
            if head.startswith("---") and _VILANDE_FM_RE.search(head):
                codes.add(path.stem.upper())
    _VILANDE_CODES = codes
    return codes


def _load_active_code_to_name() -> dict[str, str]:
    """Bygg ``kurskod → kanoniskt kursnamn`` från vaultens aktiva kursplaner.

    Används för att jämföra alias-texten i en utbildningsplans wikilink-bullet
    mot kursens officiella namn — så att programtext som avviker från
    kursplanens namn kan lyftas för administrativ rättning."""
    global _ACTIVE_CODE_TO_NAME
    if _ACTIVE_CODE_TO_NAME is not None:
        return _ACTIVE_CODE_TO_NAME
    mapping: dict[str, str] = {}
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
            fm = head[3:end]
            if _DRAFT_LINE_RE.search(fm):
                continue  # nedlagd/opublicerad — hör inte hemma i det aktiva indexet
            m = name_re.search(fm)
            if m:
                mapping[path.stem.upper()] = m.group(1).strip()
    _ACTIVE_CODE_TO_NAME = mapping
    return mapping


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
            fm = head[3:end]
            if _DRAFT_LINE_RE.search(fm):
                continue  # nedlagd/opublicerad — hör inte hemma i det aktiva indexet
            m = name_re.search(fm)
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
    r'^\s*-\s*\[\[([A-ZÅÄÖ0-9]+)\|([^\]]+)\]\]\s*,\s*([\d.,]+\s*hp)',
    re.I,
)
_BULLET_NOGRAPH = re.compile(
    r'^\s*-\s*<a class="no-graph" href="([A-ZÅÄÖ0-9]+)">([^<]+)</a>\s*,\s*([\d.,]+\s*hp)',
    re.I,
)
# Plain-text bullet kräver ``, N hp`` i slutet och avvisar wikilink/anchor.
# `\s+` (inte `\s*`) efter bindestrecket så att negativ-lookahead inte kan
# kringgås via backtracking när raden börjar med `- [[` eller `- <a`.
_BULLET_PLAIN = re.compile(
    r'^\s*-\s+(?![\[<])(.+?)\s*,\s*(\d+(?:[,.]\d+)?\s*hp)\s*$',
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
            name = m.group(1).strip()
            # Filtrera bort spöke-bullets från trasig du.se-rendering:
            # - KFTKG: bullet ``- 7, 5 hp`` blir kvar när rubriken ``**Manus
            #   för TV och film 5 …,**`` står ovanför — namnet blir bara ett
            #   tal.
            # - VBSKA: bullet ``- ) kurser som krävs för magisterexamen,
            #   60 hp`` har en föräldralös ``)`` som startar raden — du.se
            #   har vikt en parentes över radslutet och endast slutet
            #   parsades som bullet.
            # Riktiga kursnamn börjar alltid på bokstav/siffra.
            if len(name) < 3 or not re.match(r"[\w\dÅÄÖåäö]", name):
                continue
            out.append({"form": "plain", "code": None,
                        "name": name, "hp": m.group(2),
                        "line": line.strip()})
    return out


# ─────────────────────────────────────────────────────────────────────────────
# Check — nedlagda referenser i utbildningsplaner
# ─────────────────────────────────────────────────────────────────────────────

# Mönsterord som signalerar att en bullet beskriver ett alternativ-/valblock
# snarare än en enskild kurs. Notera att ` / ` inte räknas som alternation —
# slash är vanligt inuti kursnamn som "CAM/CNC", "CAD/CAM", och hanteras av
# slash-normaliseringen vid matchning istället.
_ALT_PATTERNS = re.compile(
    r"\b(eller|alternativt|valbar|valbara|valbart)\b",
    re.I,
)

# Indikatorer på att raden trunkerats (oavslutad parentes/snedstreck).
_TRUNCATED_PATTERNS = (
    lambda s: s.count("(") != s.count(")"),
    lambda s: s.endswith((" eller", " och", ",", "/")),
)


# Generiska beskrivningar som du.se använder i programlistor men som inte är
# namngivna kurser ("Valbar Inriktningskurs", "Examensarbete i ämne 1 eller 2",
# "Studenterna väljer valfria kurser …"). Vi kan aldrig länka dem och de bör
# inte heller flaggas — de är legitim programtext om val.
# Lagras i aggressiv-normaliserad form för matchning.
_BULLET_EXKLUDERAD_RAW = {
    "Examensarbete i ämne 1 eller 2",
    "Valbar Inriktningskurs",
    "Valfri kurs",
    "Obligatoriska kurser",
    "Valbara eller valfria litteraturvetenskapligt inriktade kurser",
    "Valbara och valfria litteraturvetenskapligt inriktade kurser",
    "Valbar eller valfri kurs inom franskspråkig litteratur",
    "Valbar eller valfri kurs inom tyskspråkig litteratur",
    "Studenterna väljer valfria kurser, i valfritt ämne nationellt eller "
    "internationellt, i enlighet med eget intresse och i samråd med "
    "programansvarig. Ett antal valfria kurser om",
    # Praktik/intern­ship — ingår i programmet men är inte en kursplan.
    "Solenergiteknikpraktik (7,5 eller",
    # Rubrikrader för 30 hp-block i SSHVG: raden namnger en *inriktning* och
    # kurserna som ingår listas som egna bullets direkt under den. Ingen
    # kursplan motsvarar rubriken.
    "Inriktning sociologi II",
    "Inriktning sociologi III",
    "Inriktning statsvetenskap II",
    "Inriktning statsvetenskap III",
    # Utbytes-/mobilitetsplatshållare — en termin utomlands, ingen kursplan.
    "Turismstudier utomlands",
    "Valbar termin (med möjlighet till internationellt utbyte eller läsning "
    "av valfri temakurs/kurser om",
}
_BULLET_EXKLUDERAD = {_aggressive(s) for s in _BULLET_EXKLUDERAD_RAW}

# Mönstret ``Ämne 1/2/3 med didaktisk inriktning I/II/III`` är en generisk
# platshållare i lärarprogrammens kurslistor — det betyder "studenten väljer
# ett ämne och läser dess didaktikkurs" och pekar inte mot någon konkret
# kursplan. Vi kan aldrig länka det och bör inte heller flagga det.
_PLACEHOLDER_BULLET_RE = re.compile(
    r"^ämne\s+\d+\s+med\s+didaktisk\s+inriktning\b", re.I,
)


# Kandidat-matchningar för olänkade bullets — när programtextens kursnamn inte
# matchar någon kurs men vi (manuellt) vet vilken kurs som sannolikt åsyftas.
# Format: ``"programtext"`` → ``"kanoniskt kursnamn"``. Den föreslagna kursen
# slås sedan upp i vaulten för att hämta kurskoden. Mappningen är medvetet
# konservativ: bara fall där vi är tämligen säkra på vad som åsyftas.
#
# ``_KANDIDAT_MATCHNINGAR_RAW`` är global — nyckeln är bara programtexten. Texter
# som betyder olika kurser i olika program hör i stället hemma i
# ``_KANDIDAT_MATCHNINGAR_PROG_RAW`` nedan, som nycklas på (programkod, text).
_KANDIDAT_MATCHNINGAR_RAW: dict[str, str] = {
    # ── IIT ──────────────────────────────────────────────────────────────────
    "Logik och matematik":                    "Logik och matematik för datavetenskap",
    "Datakommunikation I":                    "Datakommunikation 1",
    "Data Storage & Management Technologies": "Data Storage and Management Technologies",
    "Finita elementmetoden i praktiken":      "Finita element metoden i praktiken",
    "Finita elementmetoden":                  "Finita element metoden i praktiken",
    "3D CAD grundkurs":                       "3D-CAD – grundkurs",
    "Underhåll och kvalitet":                 "Industriell ekonomi - underhåll och kvalitet",
    "Design av PV hybrid system":             "Design av PV- och hybridsystem",
    "Examensarbete för högskoleexamen inom maskinteknik": "Examensarbete för högskoleexamen i maskinteknik",
    "Additiv tillverkning":                               "Additiv tillverkning (3D printing)",
    "Fysisk planering III – genomförande och planeringsjuridik": "Fysisk planering III - genomförande och juridisk fördjupning",
    # ── IHV ──────────────────────────────────────────────────────────────────
    "Gravididet, förlossning och postpartumvård 1": "Graviditet, förlossning och postpartumvård I",
    "Gravididet, förlossning och postpartumvård 2": "Graviditet, förlossning och postpartumvård II",
    "Strategier för implementering av förbättringsarbete i hälso-sjukvård": "Strategier för implementering av förbättringsarbete i hälso- och sjukvård",
    "Media och kommunikation inom idrott":     "Medier och kommunikation inom idrott",
    "Personcentrerad vård av personer med demens": "Personcentrerad vård för personer med demens",
    # ── IKS ──────────────────────────────────────────────────────────────────
    "Digitalefterbearbetning av ljud och bild": "Digital efterbearbetning av ljud och bild",
    "Konceptutveckling inom medieproduktion i Ljud- och musikproduktion": "Konceptutveckling inom medieproduktion för Ljud- och musikproduktion",
    "Arbetsplatsförlagd utbildning för medieproduktion": "Arbetsplatsförlagd utbildning i medieproduktion",
    "Makroekonomi introduktion":               "Makroekonomi, introduktion",
    "Mikroekonomi introduktion":               "Mikroekonomi, introduktion",
    "Makroekonomi fortsättning":               "Makroekonomi, fortsättning",
    "Mikroekonomi fortsättningskurs":          "Mikroekonomi, fortsättningskurs",
    "Samhällsekonomisk utvärdering av offentliga projekt": "Samhällsekonomisk utvärdering av offentliga projekt (Cost-Benefit Analysis)",
    "Samhällsvetenskapliga metoder II inriktning statsvetenskap": "Samhällsvetenskapliga metoder II - inriktning statsvetenskap",
    "Studier i Internationell Human Resource Management": "Studier i International Human Resource Management",
    "Personalarbete med praktik":              "Personalarbete - med praktik",
    "Entreprenörskap - entreprenörskapets villkor och särart": "Entreprenörskap - villkor och särart",
    "Förhandlings  försäljnings  och dialogkonst": "Försäljnings-, förhandling- och dialogkonst",
    "Magisterprojektets planering":            "Afrikanska studier: Forskningsprojektets planering",
    "Den vidareutvecklade uppsatsplanen":      "Afrikanska studier: Den vidareutvecklade forskningsplanen",
    "Islam och muslimska samhällen i Afrika":  "Afrikanska studier: Islam och islamiska samhällen i Afrika",
    # ── Lärarutbildning (IKS + ISLL delar programkurser) ──────────────────────
    "Didaktik och ledarskap för ämneslärare inriktning gymnasieskolan": "Didaktik och ledarskap för ämneslärare inriktning gymnasieskolan (inkl 7,5 hp VFU)",
    "Didaktik och ledarskap i förskoleklass och grundskolans åk 1–3": "Didaktik och ledarskap i förskoleklass och grundskolans årskurs 1-3 (inkl 7,5 hp VFU)",
    "Didaktik och ledarskap i grundskolans åk 4–6": "Didaktik och ledarskap i grundskolans årskurs 4-6 (inkl 7,5 hp VFU)",
    "Utvärdering och utvecklingsarbete i förskoleklass och grundskolans åk 1–3": "Utvärdering och utvecklingsarbete i förskoleklass och grundskolans åk 1-3 (varav 7,5 hp VFU)",
    "Utvärdering och utvecklingsarbete i grundskolans åk 4–6": "Utvärdering och utvecklingsarbete i grundskolans åk 4-6, (varav 7,5 hp VFU)",
    "Utvärdering och utvecklingsarbete för ämneslärare": "Utvärdering och utvecklingsarbete i grundskolans åk 7-9 och gymnasieskolan",
    "Sociala relationer, konflikter och makt - ämneslärare": "Sociala relationer, konflikter och makt i grundskolan åk 7-9 och gymnasieskolan",
    "Utveckling och lärande för ämneslärare inriktning åk 7-9": "Utveckling och lärande för ämneslärare inriktning åk 7-9 (varav 7,5 hp VFU)",
    "Examensarbete för grundlärarexamen inriktning 4–6 – del 1": "Examensarbete för grundlärarexamen inriktning 4-6 del 1",
    "Examensarbete för grundlärarexamen inriktning 4–6 – del 2": "Examensarbete för grundlärarexamen inriktning 4-6 del 2",
    "Engelska för grundlärare åk 4-6 1A":      "Engelska för grundlärare åk 4-6, 1A",
    "Engelska för grundlärare åk 4-6 1B":      "Engelska för grundlärare åk 4-6, 1B",
    "_Examensarbete i matematik för ämneslärarexamen inriktning grundskolans årskurs 7–9": "Examensarbete i matematik för ämneslärarexamen inriktning grundskolans årskurs 7-9",
    "Undervisning och ledarskap":              "Undervisning och ledarskap (varav 10 hp VFU)",
    "Ämnesdidaktik och specialpedagogik":      "Ämnesdidaktik och specialpedagogik (varav 10 hp VFU)",
    "Professionellt lärarskap och skolutveckling": "Professionellt lärarskap och skolutveckling (varav 10 hp VFU)",
    # ── ISLL ─────────────────────────────────────────────────────────────────
    "Kärnområden i tillämpad engelsk lingvistik": "Kärnområden inom tillämpad engelsk lingvistik",
    "Svenska som andraspråk i ett utvecklingsperspektiv - vetenskapsteoretiska förklaringsmodeller och metodologiska perspektiv": "Svenska som andraspråk i ett utvecklingsperspektiv - förklaringsmodeller och metodologiska perspektiv",
    # Hängande kommatecken i du.se-exporten (``… åk 4–6,, 15 hp``) — namnet
    # normaliseras redan, men kursplanens VFU-parentes måste överbryggas här.
    "Sociala relationer, konflikter och makt i grundskolan åk 4–6": "Sociala relationer, konflikter och makt i grundskolan åk 4-6 (varav 7,5 hp VFU)",
    "Vetenskapsteori och utbildningsvetenskaplig forskning för ämneslärare årskurs 7–9": "Vetenskapsteori och utbildningsvetenskaplig forskning för ämneslärare",
}
_KANDIDAT_MATCHNINGAR: dict[str, str] = {
    _aggressive(k): v for k, v in _KANDIDAT_MATCHNINGAR_RAW.items()
}

# Programspecifika kandidat-matchningar: (programkod, programtext) → kursnamn.
# Samma text kan syfta på olika kurser i olika program, typiskt i lärar-
# programmen där en generisk rad ("… - ämneslärare") betyder åk 7-9-varianten i
# ett program och gymnasievarianten i ett annat. Slås upp före den globala
# tabellen.
_KANDIDAT_MATCHNINGAR_PROG_RAW: dict[tuple[str, str], str] = {
    # Ämneslärare åk 7-9 — LP79A listar dessutom kursen två gånger, både under
    # det generiska och det fullständiga namnet.
    ("LP79A", "Utveckling och lärande - ämneslärare"): "Utveckling och lärande för ämneslärare inriktning åk 7-9 (varav 7,5 hp VFU)",
    ("LG79A", "Utveckling och lärande - ämneslärare"): "Utveckling och lärande för ämneslärare inriktning åk 7-9 (varav 7,5 hp VFU)",
    ("LP79A", "Verksamhetsförlagd utbildning - ämneslärare"): "Verksamhetsförlagd utbildning i grundskolan årskurs 7-9",
    ("LG79A", "Verksamhetsförlagd utbildning - ämneslärare"): "Verksamhetsförlagd utbildning i grundskolan årskurs 7-9",
    # Ämneslärare gymnasieskolan
    ("LPGYA", "Utveckling och lärande - ämneslärare"): "Utveckling och lärande för ämneslärare inriktning gymnasieskolan (varav 7,5 hp VFU)",
    ("LGGYA", "Utveckling och lärande - ämneslärare"): "Utveckling och lärande för ämneslärare inriktning gymnasieskolan (varav 7,5 hp VFU)",
    ("LPGYA", "Verksamhetsförlagd utbildning - ämneslärare"): "Verksamhetsförlagd utbildning i gymnasieskolan",
    ("LGGYA", "Verksamhetsförlagd utbildning - ämneslärare"): "Verksamhetsförlagd utbildning i gymnasieskolan",
}
_KANDIDAT_MATCHNINGAR_PROG: dict[tuple[str, str], str] = {
    (p.upper(), _aggressive(k)): v
    for (p, k), v in _KANDIDAT_MATCHNINGAR_PROG_RAW.items()
}


def _classify_unlinked_bullet(name: str, active: set, index: "NedlagdaIndex") -> str:
    """Klassa ett olänkat kursnamn till en av:

    - ``exkluderad``       — generisk programtext, inte en kurs (filtreras bort)
    - ``scraper-miss``     — kursnamnet finns aktivt; vår scraper kunde inte länka
    - ``program-alternativ``— bullet beskriver ett val ("X eller Y") eller "valbar"
    - ``trunkerad-rad``    — oavslutad parentes eller hängande konjunktion
    - ``nedlagd``          — kursnamnet matchar en nedlagd kursplan
    - ``okand-kurs``       — inget av ovan; sannolikt felstavning eller obefintlig kurs
    """
    if _aggressive(name) in _BULLET_EXKLUDERAD:
        return "exkluderad"
    if _PLACEHOLDER_BULLET_RE.match(name.strip()):
        return "exkluderad"
    # Prosa-stycken på 150+ tecken är fritext om utbildningen, inte en
    # kursrad — de fångas oftast bara för att raden råkar sluta på ``, N hp``
    # någonstans (t.ex. ``Vid Högskolan Dalarna är examensarbetet …
    # Vetenskapsteori och utbildningsvetenskaplig forskning, 7,5 hp``).
    if len(name) > 150:
        return "exkluderad"
    if _aggressive(name) in active:
        return "scraper-miss"
    if any(test(name) for test in _TRUNCATED_PATTERNS):
        return "trunkerad-rad"
    if _ALT_PATTERNS.search(name):
        return "program-alternativ"
    if index.lookup_name(name):
        return "nedlagd"
    return "okand-kurs"


def check_olänkade_kursreferenser(files: list[Path]) -> list[dict]:
    """Flaggar olänkade kursbullets i utbildningsplaner och klassar varför.

    Kompletterar ``check_nedlagda_refs_utb`` genom att också rapportera fall där
    en kurs *finns aktivt* men programmet inte länkar till den (scraper-bug),
    samt fall där kursnamnet inte alls kan matchas mot HDa:s katalog (okänd
    kurs — sannolikt felstavning eller obefintlig kurs som programmet hänvisar
    till). Alternativ-bullets ("X eller Y") och trunkerade rader särskiljs så
    att de inte drunknar i bruset."""
    index = load_index()
    active_titles = _load_active_titles()
    findings: list[dict] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        prog_code = path.stem
        for bullet in scan_programme_bullets(text):
            if bullet["form"] != "plain":
                continue
            kind = _classify_unlinked_bullet(bullet["name"], active_titles, index)
            if kind == "exkluderad":
                # Generisk programtext (val/valfri/textstycke) — inte en kurs.
                continue
            if kind == "nedlagd":
                # Hanteras av check_nedlagda_refs_utb — undvik dubbletter.
                continue
            check_label = {
                "scraper-miss":        "olänkad-scraper-miss",
                "program-alternativ":  "olänkad-alternativbullet",
                "trunkerad-rad":       "olänkad-trunkerad-rad",
                "okand-kurs":          "olänkad-okand-kurs",
            }[kind]
            detail = f"`{bullet['name']}` ({bullet['hp']})"
            # Vid "okand-kurs": föreslå sannolik kurskandidat om vi har en
            # manuellt curerad mappning. Om kandidaten kan lösas till en aktiv
            # kurskod omklassas fyndet till "programtext-skiljer-kursnamn" —
            # kursen finns men heter annorlunda i utbildningsplanen.
            if kind == "okand-kurs":
                agg_name = _aggressive(bullet["name"])
                suggestion = _KANDIDAT_MATCHNINGAR_PROG.get(
                    (prog_code.upper(), agg_name)
                ) or _KANDIDAT_MATCHNINGAR.get(agg_name)
                if suggestion:
                    code_to_name = _load_active_code_to_name()
                    vilande = _load_vilande_codes()
                    # Flera kurskoder kan bära samma kursnamn (en vilande äldre
                    # variant + en aktiv). Föreslå alltid den aktiva.
                    by_agg: dict[str, str] = {}
                    for code, name in code_to_name.items():
                        key = _aggressive(name)
                        prev = by_agg.get(key)
                        if prev is None or (prev in vilande and code not in vilande):
                            by_agg[key] = code
                    sugg_code = by_agg.get(_aggressive(suggestion))
                    if sugg_code:
                        detail += (
                            f" — sannolikt avses `{suggestion}` "
                            f"(kurskod `{sugg_code}`)"
                        )
                        check_label = "programtext-skiljer-kursnamn"
            findings.append({
                "check": check_label,
                "code": prog_code,
                "subj": "Utbildningsplan",
                "detail": detail,
            })
    return findings


_DASH_VARIANTS_RE = re.compile(r"[–—]")
# Kursnamn på ämneslärarprogrammen bär ofta en hp-uppdelning i slutet:
# ``Sociala relationer, konflikter och makt … åk 1-3 (varav 7,5 hp VFU)``.
# Programtexten utelämnar parantesen — bägge former syftar på samma kurs,
# så vi strippar paretensen vid jämförelse.
_VFU_HP_PAREN_RE = re.compile(
    r"\s*\((?:varav|inkl\.?|inklusive)\s+[\d,.]+\s*hp\s+vfu\)\s*$",
    re.I,
)
# Ämnes-prefix på formen ``Afrikanska studier: …`` eller ``Tyska: …`` —
# kursplanens kanoniska namn bär prefixet, men utbildningsplanens bullet
# refererar bara till suffixet. Skrapan har redan länkat dem rätt via
# colon-prefix-matchning; vi vill inte flagga den lagliga förkortningen
# som en text-avvikelse.
_SUBJECT_PREFIX_RE = re.compile(r"^[a-zåäö][a-zåäö\s]+?:\s+", re.I)


def _normalize_for_display_compare(s: str) -> str:
    """Whitespace- och dash-normaliserande jämförelseform.

    Kollapsar alla whitespace-tecken (inkl. non-breaking space ``\\xa0`` som
    du.se ofta sprider in via HTML-export) till ett enda vanligt mellanslag,
    normaliserar en-dash/em-dash (``–``/``—``) till vanligt bindestreck ``-``,
    lowercase och strip. Hyphens-saknad eller ord-skillnader flaggas
    fortfarande — bara dash-varianter och osynliga encoding-skillnader
    filtreras bort (administrationen kan inte agera på dem).

    Strippar även:
    - **Soft hyphen (U+00AD)** — osynligt tecken som inte ska räknas som
      en visuell skillnad.
    - **Huvudområde-suffixet** (``- Huvudområde Omvårdnad``) — administrativ
      stämpel som IHV-CMS:t lägger på utan att programansvarig kan ta bort.
    - **Ämnes-prefix på kursplanens namn** (``Afrikanska studier: X`` →
      ``X``) — skrapan länkar redan via colon-prefix-uppslag, så
      programtextens kortform är legitim."""
    # Soft hyphen är "potentiell bindestreck" — kursplanens namn skriver
    # ofta en vanlig ``-`` i samma position (``musik- och ljuddesign``).
    # För visuell jämförelse räknas U+00AD som ekvivalent med ``-``.
    s = _SOFT_HYPHEN_RE.sub("-", s)
    s = _DASH_VARIANTS_RE.sub("-", s)
    s = _MULTI_WS_RE.sub(" ", s).strip().lower()
    s = _HUVUDOMRADE_SUFFIX_RE.sub("", s).strip()
    s = _VFU_HP_PAREN_RE.sub("", s).strip()
    s = _SUBJECT_PREFIX_RE.sub("", s)
    return s


def check_programtext_skiljer_kursnamn(files: list[Path]) -> list[dict]:
    """Flaggar utbildningsplaner där en länkad kurs-bullet använder ett annat
    kursnamn än kursplanens kanoniska ``kursnamn:``.

    Triggas främst av svensk ellipsis i sammansättningar — programmet skriver
    "System- och verksamhetsutveckling" medan kursplanens egen titel är
    "System och verksamhetsutveckling" (utan bindestrecket). Skrapan lyckas
    ändå länka via aggressiv normalisering, men programtexten bör uppdateras
    så att studenter ser samma namn på utbildningsplanen som på kursplanen.

    Skillnaden granskas case-insensitive och whitespace-tolerant (inkl. NBSP);
    osynliga encoding-skillnader filtreras bort så att bara visuellt skiljande
    text-avvikelser flaggas."""
    code_to_name = _load_active_code_to_name()
    findings: list[dict] = []
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except OSError:
            continue
        prog_code = path.stem
        for bullet in scan_programme_bullets(text):
            if bullet["form"] not in ("wikilink", "nograph"):
                continue
            code = (bullet["code"] or "").upper()
            canonical = code_to_name.get(code)
            if not canonical:
                continue  # länkad mot okänd kurs — fångas av annan check
            shown = bullet["name"].strip()
            norm_shown = _normalize_for_display_compare(shown)
            norm_canonical = _normalize_for_display_compare(canonical)
            if norm_shown == norm_canonical:
                continue
            # Programtext utökar ofta kursnamnet med en undertitel efter
            # kolon: ``Svenska 1 för grundlärare 4–6: Barns språkutveckling
            # …``. Kursplanens egen titel är bara prefixet ``Svenska 1 för
            # grundlärare 4-6``. Om prefixet matchar kanoniska namnet räknas
            # det inte som en avvikelse — undertiteln är legitim
            # programtext-utvidgning.
            if ":" in norm_shown:
                shown_prefix = norm_shown.split(":", 1)[0].strip()
                if shown_prefix == norm_canonical:
                    continue
            findings.append({
                "check": "programtext-skiljer-kursnamn",
                "code": prog_code,
                "subj": "Utbildningsplan",
                "detail": (
                    f"Programtext `{shown}` ≠ kursplanens namn "
                    f"`{canonical}` (kurskod `{code}`)"
                ),
            })
    return findings


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
                f"(nedlagd {ned_date}) — {reason}"
            )
            findings.append({
                "check": "nedlagd-kursreferens",
                "code": prog_code,
                "subj": "Utbildningsplan",
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

# Brytpunkter som signalerar att kursnamnet börjar efter detta. ``och`` är
# medvetet utelämnad — konjunktionen förekommer ofta inuti kursnamn
# ("Vetenskapsteori och utbildningsvetenskaplig forskning för ämneslärare")
# och listseparatorn är i praktiken alltid ``samt`` eller ``,`` (varje post
# har sitt eget ``, N hp``).
_CANDIDATE_BREAK = re.compile(
    r"\b(?:inklusive|kursen|kurserna|samt)\s+|[,;:]\s+|^\s*-\s+",
    re.I | re.M,
)

# Fallback-brytpunkt som även klyver vid ``och`` — används bara om den
# obrutna kandidaten varken matchar aktivt kursindex eller nedlagda-cachen.
_CANDIDATE_BREAK_OCH = re.compile(
    r"\b(?:inklusive|kursen|kurserna|samt|och)\s+|[,;:]\s+|^\s*-\s+",
    re.I | re.M,
)


def _candidate_phrases(prereq_text: str, hp_pos: int) -> list[str]:
    """Returnera möjliga kursnamn omedelbart före ``hp_pos`` i texten.

    Vi tar de senaste 120 tecknen och klyver vid kända brytpunkter. Den
    obrutna varianten testas först (längsta först) så att hela kursnamn
    som "Vetenskapsteori och utbildningsvetenskaplig forskning för
    ämneslärare" bevaras — annars hade ``och``-splitten lämnat oss med
    bara "Vetenskapsteori" och felaktigt pekat på den nedlagda GPG263. Som
    fallback testas också ``och``-splitten för fall där "och" faktiskt
    separerar två distinkta kurser.
    """
    start = max(0, hp_pos - 120)
    chunk = prereq_text[start:hp_pos].rstrip(" ,;:")

    def _collect(pattern: re.Pattern[str]) -> list[str]:
        out: list[str] = []
        for piece in pattern.split(chunk):
            cand = piece.strip(" ,;:.")
            if not cand or len(cand) < 4:
                continue
            # Kursnamn börjar i regel med versal eller siffra ("3D CAD …").
            if not (cand[0].isupper() or cand[0].isdigit()):
                continue
            out.append(cand)
        return out

    seen: set[str] = set()
    candidates: list[str] = []
    for cand in _collect(_CANDIDATE_BREAK) + _collect(_CANDIDATE_BREAK_OCH):
        if cand in seen:
            continue
        seen.add(cand)
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
