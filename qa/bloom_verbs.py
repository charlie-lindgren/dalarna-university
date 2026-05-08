"""Svenskt Bloom-verb-lexikon (revidered taxonomi, 2001).

Sex nivåer:
    1. Minnas       (Remember)
    2. Förstå       (Understand)
    3. Tillämpa     (Apply)
    4. Analysera    (Analyse)
    5. Värdera      (Evaluate)
    6. Skapa        (Create)

Verben lagras i infinitiv + presens. Lärandemål följer nästan alltid
mönstret "Efter godkänd kurs ska studenten kunna [INF]" så infinitiv-
formerna täcker den största delen, men presens läggs till för säkerhets
skull (kursplaner som formulerar målen utan modalverb).

Dubbelplacerade verb (t.ex. *jämföra* förekommer hos både Förstå och
Analysera i litteraturen) placeras på den nivå som dominerar i
Anderson & Krathwoll 2001 / KTH:s Blomma. Lexikonet utökas iterativt
via `bloom-okant-verb`-fynd från `qa/check_kursplaner.py`.
"""

from __future__ import annotations

# Nivå → mängd verb (infinitiv + presens, lowercase, utan accent-skillnader)
BLOOM_VERBS: dict[int, set[str]] = {
    1: {  # Minnas — återge fakta utan tolkning
        "minnas", "minns",
        "redogöra", "redogör",
        "beskriva", "beskriver",
        "definiera", "definierar",
        "namnge", "namnger",
        "identifiera", "identifierar",
        "lista", "listar",
        "återge", "återger",
        "ange", "anger",
        "repetera", "repeterar",
        "citera", "citerar",
        "memorera", "memorerar",
        "räkna", "räknar",
        "uppvisa", "uppvisar",
        "visa", "visar",  # i bemärkelsen "visa kunskap"
        "känna", "känner",
        "nämna", "nämner",
        "uppge", "uppger",
        "återkalla", "återkallar",
        "ha", "har",  # "ha kunskap om" — vanligt inledningsverb
        "läsa", "läser",
        "redovisa", "redovisar",
        "påvisa", "påvisar",
        "söka", "söker",
        "samla", "samlar",
        "ge", "ger",  # "ge exempel på"
        "föra", "för",  # "föra resonemang om"
        "nämna", "nämner",
        "presentera", "presenterar",
    },
    2: {  # Förstå — tolka och sammanfatta innebörd
        "förstå", "förstår",
        "förklara", "förklarar",
        "sammanfatta", "sammanfattar",
        "tolka", "tolkar",
        "klassificera", "klassificerar",
        "jämföra", "jämför",
        "exemplifiera", "exemplifierar",
        "illustrera", "illustrerar",
        "diskutera", "diskuterar",
        "översätta", "översätter",
        "rapportera", "rapporterar",
        "uttrycka", "uttrycker",
        "beräkna", "beräknar",  # gränsfall mot Tillämpa, men ofta "förstå-räkna"
        "associera", "associerar",
        "generalisera", "generaliserar",
        "matcha", "matchar",
        "parafrasera", "parafraserar",
        "predicera", "predicerar",
        "skriva", "skriver",
        "tala", "talar",
        "kommunicera", "kommunicerar",
        "kommentera", "kommenterar",
        "resonera", "resonerar",
        "sammanställa", "sammanställer",
        "redogöra för", "redogör för",
        "behärska", "behärskar",
        "observera", "observerar",
        "interagera", "interagerar",
        "delta", "deltar",
        "samarbeta", "samarbetar",
    },
    3: {  # Tillämpa — använda kunskap i nya situationer
        "tillämpa", "tillämpar",
        "använda", "använder",
        "genomföra", "genomför",
        "lösa", "löser",
        "demonstrera", "demonstrerar",
        "implementera", "implementerar",
        "utföra", "utför",
        "verkställa", "verkställer",
        "operera", "opererar",
        "manövrera", "manövrerar",
        "modifiera", "modifierar",
        "konfigurera", "konfigurerar",
        "förbereda", "förbereder",
        "producera", "producerar",
        "praktisera", "praktiserar",
        "schemalägga", "schemalägger",
        "göra", "gör",
        "hantera", "hanterar",
        "ta", "tar",  # "ta ansvar för", "ta ställning"
        "arbeta", "arbetar",
        "dimensionera", "dimensionerar",
        "framställa", "framställer",
        "bearbeta", "bearbetar",
        "ställa", "ställer",  # "ställa upp en modell"
        "sätta", "sätter",  # "sätta in i kontext"
        "bestämma", "bestämmer",
        "upprätta", "upprättar",
        "anpassa", "anpassar",
        "mäta", "mäter",
        "stödja", "stödjer",
        "vårda", "vårdar",
        "uttala", "uttalar",
        "följa", "följer",
        "utöva", "utövar",
        "bedriva", "bedriver",
    },
    4: {  # Analysera — bryta ner i delar och se samband
        "analysera", "analyserar",
        "granska", "granskar",
        "urskilja", "urskiljer",
        "strukturera", "strukturerar",
        "dekomponera", "dekomponerar",
        "undersöka", "undersöker",
        "utreda", "utreder",
        "kontrastera", "kontrasterar",
        "härleda", "härleder",
        "diagnostisera", "diagnostiserar",
        "differentiera", "differentierar",
        "dela", "delar",
        "organisera", "organiserar",
        "relatera", "relaterar",
        "testa", "testar",
        "experimentera", "experimenterar",
        "kategorisera", "kategoriserar",
        "särskilja", "särskiljer",
        "problematisera", "problematiserar",
        "förhålla", "förhåller",  # "förhålla sig kritiskt till"
        "reflektera", "reflekterar",  # gränsfall mot Värdera; placeras på Analysera
    },
    5: {  # Värdera — göra bedömningar utifrån kriterier
        "värdera", "värderar",
        "bedöma", "bedömer",
        "motivera", "motiverar",
        "argumentera", "argumenterar",
        "försvara", "försvarar",
        "rekommendera", "rekommenderar",
        "utvärdera", "utvärderar",
        "kritisera", "kritiserar",
        "döma", "dömer",
        "rättfärdiga", "rättfärdigar",
        "validera", "validerar",
        "verifiera", "verifierar",
        "kontrollera", "kontrollerar",
        "prioritera", "prioriterar",
        "välja", "väljer",
        "rangordna", "rangordnar",
        "avgöra", "avgör",
        "pröva", "prövar",
        "bevisa", "bevisar",
    },
    6: {  # Skapa — sätta samman delar till nytt helt
        "skapa", "skapar",
        "utforma", "utformar",
        "konstruera", "konstruerar",
        "designa", "designar",
        "utveckla", "utvecklar",
        "planera", "planerar",
        "formulera", "formulerar",
        "syntetisera", "syntetiserar",
        "generera", "genererar",
        "föreslå", "föreslår",
        "uppfinna", "uppfinner",
        "komponera", "komponerar",
        "kombinera", "kombinerar",
        "integrera", "integrerar",
        "modellera", "modellerar",
        "rita", "ritar",
        "hypotisera", "hypotiserar",
        "uppföra", "uppför",
        "författa", "författar",
        "initiera", "initierar",
        "bidra", "bidrar",  # "bidra till utveckling av"
        "färdigställa", "färdigställer",
        "prognostisera", "prognostiserar",
    },
}


# Inverterad uppslagsmappning verb → nivå. Vid dubbelregistrering
# (samma verb i flera nivåer) väljs den högsta nivån — det matchar
# Bloom-litteraturens praxis att "räkna upp" till mer avancerade
# tillämpningar när kontexten kan tolkas i flera riktningar.
_VERB_TO_LEVEL: dict[str, int] = {}
for _level, _verbs in BLOOM_VERBS.items():
    for _v in _verbs:
        # Behåll högsta nivån vid kollision
        if _v not in _VERB_TO_LEVEL or _VERB_TO_LEVEL[_v] < _level:
            _VERB_TO_LEVEL[_v] = _level


def bloom_level(verb: str) -> int | None:
    """Returnera Bloom-nivå (1–6) för verbet, eller None om okänt."""
    return _VERB_TO_LEVEL.get(verb.lower().strip())
