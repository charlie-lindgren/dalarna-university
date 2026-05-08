"""
Delade hjälpare och kontroller som används av både check_kursplaner.py och
check_utbildningsplaner.py.

Innehåller:
  * Textparsning (frontmatter, sektionsutdrag, markdown-strippning)
  * Path-helpers (course_code, subject)
  * De fyra språk-/stavningskontroller som är gemensamma för kurs- och
    utbildningsplaner: dubblerade ord, kända felstavningar, hunspell sv,
    hunspell en.
  * Rapportbyggare (build_report)
"""

import os
import re
import subprocess
from collections import defaultdict
from datetime import date
from pathlib import Path

DICPATH = os.path.expanduser("~/Library/Spelling")


# ─────────────────────────────────────────────────────────────────────────────
# Hjälpare
# ─────────────────────────────────────────────────────────────────────────────

def strip_frontmatter(text: str) -> str:
    if text.startswith("---"):
        end = text.find("\n---", 3)
        if end != -1:
            return text[end + 4:]
    return text


def extract_section(text: str, heading: str) -> str:
    pattern = re.compile(
        r"^## " + re.escape(heading) + r"\s*\n(.+?)(?=^## |\Z)",
        re.MULTILINE | re.DOTALL,
    )
    m = pattern.search(text)
    return m.group(1) if m else ""


def remove_markdown(text: str) -> str:
    text = re.sub(r"\[.*?\]\(.*?\)", " ", text)
    text = re.sub(r"\[\[.*?\]\]", " ", text)
    text = re.sub(r"https?://\S+", " ", text)
    text = re.sub(r"[#*_`\[\]|>]", " ", text)
    text = re.sub(r"\b\S*\d\S*\b", " ", text)
    return text


def course_code(path: Path) -> str:
    return path.stem


def subject(path: Path) -> str:
    return path.parent.name


# ─────────────────────────────────────────────────────────────────────────────
# Check 1 — Dubblerade ord
# ─────────────────────────────────────────────────────────────────────────────
DUP_WORD_RE = re.compile(r"\b(\w{2,})[ \t]+\1\b", re.IGNORECASE)
DUP_IGNORE = {"för", "och", "med", "om", "av", "till", "i", "på", "de", "det"}


def check_dup_words(files: list[Path]) -> list[dict]:
    findings = []
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        for m in DUP_WORD_RE.finditer(body):
            word = m.group(1).lower()
            if word in DUP_IGNORE:
                continue
            line = body[max(0, m.start() - 60): m.end() + 60].replace("\n", " ").strip()
            findings.append({
                "check": "dubblerat-ord",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"`{m.group(1)}` — …{line}…",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 2 — Kända felstavningar
# ─────────────────────────────────────────────────────────────────────────────
KNOWN_TYPOS = {
    r"adminstrat": "administrativa/administration",
    r"infomation": "information",
    r"såväll": "såväl",
    r"tilsammans": "tillsammans",
}


def check_known_typos(files: list[Path]) -> list[dict]:
    findings = []
    patterns = [(re.compile(pat, re.IGNORECASE), corr)
                for pat, corr in KNOWN_TYPOS.items()]
    for p in files:
        body = strip_frontmatter(p.read_text(encoding="utf-8"))
        body_sv = re.sub(r"\n## English Version.+", "", body, flags=re.DOTALL)
        for rx, corr in patterns:
            if rx.search(body_sv):
                findings.append({
                    "check": "känd-felstavning",
                    "code": course_code(p),
                    "subj": subject(p),
                    "detail": f"`{rx.pattern}` → {corr}",
                })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 3 — Hunspell svenska
# ─────────────────────────────────────────────────────────────────────────────
SV_IGNORE = {
    "course","name","mathematics","engineering","project","thesis","analysis",
    "construction","degree","planning","energy","development","education",
    "teachers","industrial","school","building","introduction","sustainable",
    "web","technology","years","primary","manufacturing","physics","structural",
    "bachelor","learning","testing","communication","computer","science",
    "electrical","master","civil","design","management","information","systems",
    "software","network","security","research","applied","advanced","basic",
    "statistics","data","digital","media","interactive","mobile","cloud",
    "database","programming","algorithms","architecture","infrastructure",
    "innovation","entrepreneurship","business","economics","leadership",
    "environment","materials","mechanics","dynamics","thermodynamics",
    "measurement","quality","production","logistics","maintenance","safety",
    "healthcare","social","psychology","pedagogy","didactics","assessment",
    "feedback","reflection","collaboration","critical","creative",
    "analytical","practical","theoretical","empirical","qualitative","quantitative",
    "academic","professional","international","national","regional","local",
    "public","private","sector","market","strategy","organization","process",
    "model","framework","method","approach","tool","technique","standard",
    "requirement","specification","documentation","deployment","support",
    "service","solution","application","platform",
    "mikrodataanalys","samhällsplanerarprogrammet","envariabelanalys",
    "flervariabelanalys","omexamination","kursansvarig","ämnesansvarig",
    "kurslitteratur","lärandemål","examinationsformer","betygsskala",
    "förkunskapskrav","arbetsformer","studenten","studerande","kursplan",
    "kursplanen","tentamen","salstentamen","inlämningsuppgift","inlämningsuppgifter",
    "dugga","seminarium","laborationer","projektarbete","examination",
    "programkurs","distanskurs","campuskurs","halvfart","helfart","kvartsfart",
    "grundnivå","forskarutbildning","doktorand","magisternivå","kandidatexamen",
    "magisterexamen","masterexamen","kandidatprogram","masterprogram",
    "civilingenjörsprogram","högskoleexamen","yrkesexamen","specialisering",
    "inriktning","samhällsbyggnad","samhällsbyggnadsteknik","samhällsplanerare",
    "produktionsteknik","byggteknik","elektroteknik","energiteknik",
    "maskinteknik","datateknik","informationsteknik","kommunikationsteknik",
    "beräkningsvetenskap","maskininlärning","dataanalys","datahantering",
    "datasäkerhet","datainsamling","datakvalitet","webbdesign","webbprogrammering",
    "webbapplikation","webbutveckling","mjukvaruutveckling","mjukvaruteknik",
    "systemutveckling","systemförvaltning","nätverkssäkerhet","cybersäkerhet",
    "informationssäkerhet","programutvecklingsteknik","objektorienterad",
    "användargränssnitt","datavetenskaper","biometriska","äkthetsbevisningar",
    "hp","ects","ht","vt","lp","svt","sfs","hda","hdu","uu","kth","ltu","lnu",
    "mdu","bth","gih","gu","su","liu","lth","fup","inkl","dvs","exkl","osv",
    "etc","bl","ca","resp","mfl","pga","tex",
    "samhälls","stjärn","räkne",
    "knäckkrafter","släntstabilitet","skärkrafter","skärparametrar","skärzonen",
    "tryckfallsberäkningar","värmekomfortbedömningar","byggnadsskalslösningar",
    "utförandeskedet","samhällsplanerarbranschen","kulturmiljövärden",
    "äkthetsbevisningssystem","äkthetsbevisningstekniker",
    "inomstrålningslära","sannolikhetsströmtäthet","schrödingerekvationen",
    "talområden","areabestämning","maskininlärningsparadigmer",
    "chi-två","chi-två-test","poissonfördelning","poissonfördelningen",
    "koordinatmätmaskin","mätdatakvaliteten","mätprojekt","mätsensorer",
    "lönsamhetsgap","säsongsvärmelager","rumsuppvärmning","temperaturnivåkrav",
    "excelberäkningar",
    "beslutsstödverktyg","datainhämtningsstrategier","iot-lösningar",
    "intelligence-lösning","ai-domänen","ai-området",
    "etjänster","etjänstebegrepp","windowsmiljö","ändutrustning",
    "graftäckning","samtanvändning","nästling","trådade",
    "utförandedel","uppnåelsen","problemlösandeprocess","förändringsbarhet",
    "cirkulärekonomiska",
    "högdimensionell","högdimensionella",
    "samläses","bps-beräkning","språklaboratoriska","förseminarieuppgifter",
    "språklabbar","göteborgs","inlärarkorpusar","marknadsföringsmixen",
    "marknadsföringsmix","hbtqi-frågor","mödra","välargumenterad",
    "rörelseverb","undervisningspråk","eu-rätt","eu-rättsliga",
    "förrättsligande","eu-rättens","prejudikatsvärde","undersökningsbart",
    "vfu-lärare","förskole",
    # Giltiga sammansättningar och fältspecifika ord som hunspell sv_SE missar
    "närstudium","mångkanalsinspelning","preparandnivå",
    "tränarskapet","träningsbarhet",
    "tyskämnet","tyskämnets","engelskämnet","engelskämnets",
    "franskämnet","franskämnets",
    "iordningsställande","medieringssätt","seriemanusförfattande",
    "färgkorrigeringstrategier","förproduceras","ljudläggs","ljudlägga",
    "dokumentärfilmfoto","dokumentärfilmfotots",
    "välfärdstjänstearbete","lässtilar",
    # Städer/orter (gemener) som kan förekomma i kursplaner
    "malmö","jönköping","örebro",
    # IIT — fältspecifika sammansättningar
    "vägprojekteringshjälpmedel","connectmöten","reellvärda",
    "böjmotstånd","affärsplanbedömningar",
}
HAS_SV = re.compile(r"[åäöÅÄÖ]")


def check_hunspell_sv(files: list[Path]) -> list[dict]:
    word_to_files: dict[str, set[Path]] = defaultdict(set)
    for p in files:
        raw = p.read_text(encoding="utf-8")
        txt = re.sub(r"\n## English Version.+", "", strip_frontmatter(raw), flags=re.DOTALL)
        txt = remove_markdown(txt)
        for w in re.findall(r"\b[a-zA-ZåäöÅÄÖ\-]{3,}\b", txt):
            lw = w.lower().strip("-")
            if lw not in SV_IGNORE and not w.isupper() and HAS_SV.search(lw):
                word_to_files[lw].add(p)

    if not word_to_files:
        return []

    proc = subprocess.run(
        ["hunspell", "-d", "sv_SE", "-i", "UTF-8", "-l"],
        input="\n".join(sorted(word_to_files)),
        capture_output=True, text=True,
    )
    unknown = {w.strip() for w in proc.stdout.splitlines() if w.strip()}
    rare = {w for w in unknown if len(word_to_files[w]) < 4}

    findings = []
    for w in sorted(rare):
        for p in sorted(word_to_files[w]):
            findings.append({
                "check": "stavning-sv",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"`{w}` (sv)",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Check 4 — Hunspell engelska
# ─────────────────────────────────────────────────────────────────────────────
EN_IGNORE = {
    "hda","iit","dalarna","uu","kth","ltu","mdu","bth",
    "java","python","sql","html","css","xml","json","yaml","api","rest","soap",
    "oop","mvc","mvvm","uml","ide","git","github","gitlab","scrum","kanban",
    "devops","paas","saas","iaas","iac","powershell","linux","macos","ios",
    "android","javascript","typescript","nodejs","reactjs","vuejs","angularjs",
    "spring","django","flask","dotnet","php","ruby","kotlin","swift","rust",
    "docker","kubernetes","terraform","ansible","jenkins","restful","http",
    "https","tcp","udp","ssh","ssl","tls","dns","dhcp","vpn","iot","ai","ml",
    "dl","llm","nlp","gan","cnn","rnn","lstm","gpt","cv","blockchain","aws",
    "azure","gcp","vm","cpu","gpu","ram","ssd","lan","wan","vlan","bgp","ospf",
    "nat","bim","cad","cfd","fem","gis","erp","crm","scm","olap","oltp",
    "nosql","acid","etl","bi","ects","hp","phd","bsc","msc","ba","ma","eg",
    "ie","etc","vs","fig","no","nr","pp","ed","eds","vol","ch",
    "bloom","biggs","bologna","nordic","swedish",
    "kursplan","lärandemål","examinator","tentamen",
    "organise","organised","organising","organisation","organisations",
    "recognise","recognised","recognising","recognisable",
    "analyse","analysed","analysing","characterise","characterised",
    "optimise","optimised","optimising","optimisation","optimisations",
    "realise","realised","realising","specialise","specialised","specialising",
    "utilise","utilised","utilising","utilisation","utilise","utilises",
    "prioritise","prioritised","prioritising","behaviour","behaviours",
    "modelling","labelling","travelling","cancelled","focussed",
    "centre","centres","centred","metre","metres","litre","litres",
    "colour","colours","coloured","colourful","favour","favours","favoured",
    "honour","labour","neighbour","programme","programmes","programmed",
    "defence","licence","practise","practises","practised",
    "mainfield","subfield","subfields","apis","photovoltaics","coursework",
    "dimensioning","dimensioned","eurocodes","geoconstructions","geotechnics",
    "loadbearing","stabilisation","stabilisations","lcas","lccas",
    "backdoors","cyber","exfiltrate","cryptographic","laborations",
    "biometric","biometrics",
    "matlab","ethernet","qos",
    "byggnad","byggteknik","produktion","psychosocial",
    "incen","tives","bps",
    "kimball","inmon","feistel","rankine","kirchhoff","tufte","dalarnas",
    "pvsyst","polysun",
    "roadmap","timeframe","lifecycle","webpage","webpages",
    "frontend","backend","cybercrime","cybercriminals","cybersecurity",
    "reusability","reproducibility","inclusivity","notational",
    "processbased","designbased",
    "eservices","geodata","geojson","topologies",
    "combinatorics","combinatorial","factorisation","hypergeometric",
    "multivariable","bivariate","perceptron","sigmoid","tabu",
    "cryptanalytic",
    "metrology","formability","machinability","remanufacturing",
    "metallographic","profilometer","microstructure",
    "biofuels","hydropower","evs","sociotechnical","multicriteria",
    "benchmarking","cartographical","locational",
    "apperception","laboration","didactics",
    "ontologisms",
    "learnt","fulfil","practising","practised","computerised","visualised",
    "summarising","scrutinising","confirmative",
    "electrochemical","electromechanical","hydronic","incompressible",
    "pipings","microclimate",
    "socio","pre",
    "arab","arabic","syrian",
    # Proper nouns — places, nationalities, religions, writing systems
    "angola","asian","australia","australian","berlin","brazil","brazilian",
    "britain","british","buddhism","cambridge","canada","caribbean","christianity",
    "cyrillic","egyptian","germanic","germany","hanzi","india","ireland","islam",
    "latin","lusophone","mozambique","oceania","philip","qing","russia","russias",
    "sahara","scandinavia","sao","slavic","slavonic","spain","verde","zeeland",
    # Named theories, economists, mathematicians, concepts
    "balagha","cantillon","cramer","hegelian","heimat","keynesian","kirzner",
    "lagrange","marxism","marxist","nobel","pareto","phillips","poisson",
    "pythagorean","schumpeter","shannon","sdgs",
    # Literary, cultural, and humanities studies
    "aesthetical","affective","assimilations","audiovisuality","bildungsroman",
    "collegial","contrastively","decolonial","dramaturgy","dramaturgical",
    "ecocriticism","encyclopaedias","epistemologies","essentialist","fieldnotes",
    "formalia","franca","hermeneutics","hybridity","interculturality","intermedial",
    "intermediality","intertextual","intertextuality","liminality","literatures",
    "microhistory","narratological","ontologies","otaku","poetological",
    "postcolonialism","postnationalism","redefinitions","roleplay","scriptwriting",
    "situationally","sociocultural","syllabi","transculturality","transformative",
    # Statistics, econometrics, mathematics
    "autocorrelation","endogeneity","geostatistical","heteroskedasticity","logit",
    "macroeconomically","multicollinearity","nonstationarity","optimality",
    "overfitting","probit","regularisation","scientificity","tobit",
    # Linguistics
    "dialectology","diatopic","diatopical","diaphasic","diglossia","englishes",
    "ideographical","languagevarieties","lexically","phonetical","romanization",
    "sociolects","sociopragmatic","sociopragmatics","synchronic","typological",
    "variationist",
    # Medical, biological, sports, health science
    "andrology","biomechanical","biomechanics","biopsychosocial","enthalpy",
    "ergogenic","ergonomical","gynaecology","humanbiology","inductors","locomotor",
    "motorical","multimorbidity","nociception","parenteral","pathogenesis",
    "personcentered","prehabilitation","promotive","psychoacoustics",
    "psycholinguistic","psycholinguistics","physiotherapeutic","salutogenesis",
    "sportpedagogy","trainability",
    # British / Commonwealth English spellings
    "actualises","ageing","behavioural","characterisation","characterises",
    "conceptualised","contextualised","contextualises","contextualising",
    "datafication","democratisation","ehealth","emphasise","emphasised",
    "emphasises","enquiry","esthetic","explorative","favourable","finalised",
    "generalise","generalised","globalised","illhealth","individualised",
    "internationalisation","laborative","maximise","mediatisation","microblogs",
    "minimisation","minimise","minimising","multimodal","normalisation",
    "operationalisation","periodisation","problematisation","problematised",
    "problematization","problematizations","problematized","problematizing",
    "realisation","regionalisation","scalable","specialisations","standardised",
    "synthesise","systematise","thematised","thematises","theorisations",
    "timeframes","urbanisation","virtualisation","visualisations","visualise",
    "visualising","wellbeing","concretize",
    # Domain compounds and other valid academic terms
    "arithmetics","datasheets","exchangers","fronter","meso","netbased",
    "opponentship","participations","projectwork","researchable","reviewable",
    "systematics","uhr",
    "childrens","continous","curriculums","eco","kerchoff","lingua","www",
    # Svenska ord som läcker in i engelsk text (klart FP)
    "som","samt","ett","det","alla","inom","kan","hur","kommer","deltar",
    "arbete","projekt","skola","modul","praxis","engelska","teknik",
    "teknikens","kurserna","delkurs","didaktik","anatomi","bedriva",
    "grundskolans","kunskaper","pedagogiskt","specialpedagogisk",
    "studenta","legitimation","physiologi","nerv",
    # Domäntermer som hunspell saknar
    "neuromuscular","poststructuralism","falsificationism","verificationism",
    "problematizes","socialisation","neuropsychiatric","chorology",
    "filmmaking","multicamera","judokas","cartographically","onwards",
    "roleplays","islamic",
    # IIT — historiska civilisationer, brittisk stavning, tekniktermer
    "babylonian","mayan","sumerian","neighbourhood","neighbourhoods",
    "cobots","bioenergy","biofuel","microsystems","insolation",
}


def check_hunspell_en(files: list[Path]) -> list[dict]:
    word_to_files: dict[str, set[Path]] = defaultdict(set)
    for p in files:
        raw = p.read_text(encoding="utf-8")
        m = re.search(r"\n## English Version\s*\n(.+)", raw, re.DOTALL)
        if not m:
            continue
        txt = remove_markdown(m.group(1))
        for w in re.findall(r"\b[a-zA-Z\-]{3,}\b", txt):
            lw = w.lower().strip("-")
            if lw not in EN_IGNORE and not w.isupper():
                word_to_files[lw].add(p)

    if not word_to_files:
        return []

    env = os.environ.copy()
    env["DICPATH"] = DICPATH
    proc = subprocess.run(
        ["hunspell", "-d", "en_US", "-i", "UTF-8", "-l"],
        input="\n".join(sorted(word_to_files)),
        capture_output=True, text=True, env=env,
    )
    unknown = {w.strip() for w in proc.stdout.splitlines() if w.strip()}
    rare = {w for w in unknown if len(word_to_files[w]) < 5}

    findings = []
    for w in sorted(rare):
        for p in sorted(word_to_files[w]):
            findings.append({
                "check": "stavning-en",
                "code": course_code(p),
                "subj": subject(p),
                "detail": f"`{w}` (en)",
            })
    return findings


# ─────────────────────────────────────────────────────────────────────────────
# Rapport
# ─────────────────────────────────────────────────────────────────────────────

NOTE = """
OBS: Denna rapport är rådata från automatisk analys. Varje rad kräver
manuell granskning. Hunspell-fynd kan vara domäntermer, brittiska stavningar
eller scrapingartefakter. AI-agenten fattar det slutliga redaktionella beslutet.
"""


def build_report(
    title: str,
    all_findings: list[dict],
    files: list[Path],
    check_labels: dict[str, str],
) -> str:
    today = date.today().isoformat()
    lines = [
        f"# {title} — {today}",
        "",
        f"Granskade filer: {len(files)}  |  Totalt fynd: {len(all_findings)}",
        "",
        NOTE.strip(),
        "",
        "---",
        "",
    ]

    by_check: dict[str, list[dict]] = defaultdict(list)
    for f in all_findings:
        by_check[f["check"]].append(f)

    for check_key, label in check_labels.items():
        rows = by_check.get(check_key, [])
        lines.append(f"## {label} ({len(rows)} fynd)")
        lines.append("")
        if rows:
            lines.append("| Kod | Ämne | Detalj |")
            lines.append("| --- | --- | --- |")
            for r in sorted(rows, key=lambda x: (x["subj"], x["code"])):
                lines.append(f"| {r['code']} | {r['subj']} | {r['detail']} |")
        else:
            lines.append("*Inga fynd.*")
        lines.append("")

    return "\n".join(lines)
