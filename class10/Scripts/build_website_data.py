# -*- coding: utf-8 -*-
"""
Build website JSON data files from the JAC Class 10 Python question bank.

For each subject we:
  1. Parse the existing *_data.py question bank (real NCERT-based questions).
  2. Add a curated fact bank of MCQs (filler_data.py).
  3. Deterministically generate additional curriculum write-type questions
     so every subject reaches the 300+ per-subject minimum.

Generator quality rules (so auto-generated questions read naturally):
  - chapter tag in "(...)" is cleaned: no "अध्याय 3:" prefixes, no trailing
    "(English)" translations, no "- 30 प्रश्न" noise.
  - each real chapter is mapped to a topic group so its generated questions
    actually belong to that chapter.
  - unmapped chapters only get subject-neutral "*" topics.
  - templates are generic enough for every topic (no "उपयोग/अनुप्रयोग").
"""
import io, json, os, re, importlib.util
from filler_data import FILLERS

BASE = r"E:\logo\class10"
OUT = r"E:\logo\class10\website\js\data"
os.makedirs(OUT, exist_ok=True)

MIN_QUESTIONS = 300

SOURCES = {
    "hindi":     os.path.join(BASE, "Hindi", "hindi_data.py"),
    "english":   os.path.join(BASE, "English", "english_data.py"),
    "maths":     os.path.join(BASE, "Mathematics", "maths_data.py"),
    "science":   os.path.join(BASE, "Science", "science_data.py"),
    "history":   os.path.join(BASE, "Social_Science", "1_Itihaas_History", "history_data.py"),
    "geography": os.path.join(BASE, "Social_Science", "2_Bhugol_Geography", "geography_data.py"),
    "civics":    os.path.join(BASE, "Social_Science", "3_Rajneeti_Civics", "civics_data.py"),
    "economics": os.path.join(BASE, "Social_Science", "4_Arthshastra_Economics", "economics_data.py"),
}

SUBJECTS_META = {
    "hindi": {"name": "हिन्दी"}, "english": {"name": "English"}, "maths": {"name": "गणित"},
    "physics": {"name": "भौतिक विज्ञान"}, "chemistry": {"name": "रसायन विज्ञान"},
    "biology": {"name": "जीव विज्ञान"}, "history": {"name": "इतिहास"},
    "geography": {"name": "भूगोल"}, "civics": {"name": "राजनीति विज्ञान"},
    "economics": {"name": "अर्थशास्त्र"},
}


def load_module(label, path):
    spec = importlib.util.spec_from_file_location(label, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


# ---------------- MCQ / Q&A parsing helpers ----------------
def extract_mcq_parts(text):
    text = str(text)
    m = re.search(r'\((क|ख|ग|घ)\)', text)
    if not m:
        return text, ["(क)", "(ख)", "(ग)", "(घ)"]
    stem = text[:m.start()].strip()
    letters = ['(क)', '(ख)', '(ग)', '(घ)']
    positions = []
    for l in letters:
        idx = text.find(l)
        if idx == -1:
            return text, [l.strip() for l in letters]
        positions.append((idx, l))
    positions.sort()
    opts = []
    for i in range(len(positions)):
        start = positions[i][0] + len(positions[i][1])
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        opts.append(text[start:end].strip().rstrip('\n'))
    return stem, opts


def parse_mcq_answer(raw_answer):
    txt = str(raw_answer)
    m = re.search(r'\(([कखगघ])\)', txt)
    if not m:
        return None, txt
    idx = ['क', 'ख', 'ग', 'घ'].index(m.group(1))
    val = re.sub(r'^\s*सही\s*उत्तर\s*[:：]?\s*', '', txt)
    val = re.sub(r'^\s*\([कखगघ]\)\s*', '', val).strip()
    return idx, val


def to_write_q(chapter, qtext, atext, nid):
    return {"id": nid, "chapter": chapter, "type": "write", "q": qtext, "ans": atext}


def to_mcq_q(chapter, qtext, opts, ansidx, ansval, nid):
    if ansidx is None:
        ansidx = 0
    return {"id": nid, "chapter": chapter, "type": "mcq", "q": qtext,
            "options": opts if opts else ["(क)", "(ख)", "(ग)", "(घ)"],
            "answer": ansidx, "ans": ansval}


class Counter:
    def __init__(self, prefix):
        self.n = 0
        self.prefix = prefix
    def nid(self):
        self.n += 1
        return f"{self.prefix}-{self.n}"


def parse_bank(path, prefix):
    """Parse a *_data.py into a list of {chapter, type, q, options/ans} dicts."""
    m = load_module(prefix, path)
    c = Counter(prefix)
    items = []
    for section in m.SECTIONS:
        chapter = section[0]
        seq = section[1]
        prev_q = None
        prev_type = None
        prev_opts = None
        for typ, txt in seq:
            txt = str(txt)
            if typ == 'S':
                continue
            if typ == 'Q':
                prev_q, prev_type, prev_opts = txt, 'Q', None
            elif typ == 'MCQ':
                stem, opts = extract_mcq_parts(txt)
                prev_q, prev_type, prev_opts = stem, 'MCQ', opts
            elif typ == 'A':
                if prev_type == 'MCQ' and prev_q:
                    ansidx, ansval = parse_mcq_answer(txt)
                    items.append(to_mcq_q(chapter, prev_q, prev_opts, ansidx, ansval, c.nid()))
                    prev_q = None
                elif prev_type == 'Q' and prev_q:
                    items.append(to_write_q(chapter, prev_q, txt, c.nid()))
                    prev_q = None
    return items


SCIENCE_CHAPTERS = {
    "chemistry": ["रासायनिक अभिक्रियाएँ और समीकरण", "अम्ल, क्षारक एवं लवण", "धातु और अधातु",
                  "कार्बन और उसके यौगिक", "तत्वों का आवर्त वर्गीकरण"],
    "physics": ["विद्युत", "मानव नेत्र एवं रंगीन संसार", "प्रकाश - परावर्तन एवं अपवर्तन",
                "विद्युत धारा का चुंबकीय प्रभाव", "ऊर्जा के स्रोत"],
    "biology": ["जैव प्रक्रम", "नियंत्रण एवं समन्वय", "जीव जनन कैसे करते हैं",
                "आनुवंशिकता एवं जैव विकास", "हमारा पर्यावरण"],
}

SCIENCE_KEYWORDS = {
    "chemistry": ["अम्ल", "क्षारक", "लवण", "धातु", "अधातु", "ऑक्सीकरण", "अपचयन", "रासायनिक अभिक्रिया",
                  "कार्बन", "आवर्त", "pH", "लिटमस", "अभिक्रिया", "संक्षारण", "अयस्क"],
    "physics": ["विद्युत", "प्रतिरोध", "ओम", "धारा", "वोल्ट", "प्रकाश", "दर्पण", "लेंस", "अपवर्तन",
                "परावर्तन", "नेत्र", "चुंबक", "शक्ति", "आवेश", "प्रतिबिंब", "वोल्टेज"],
    "biology": ["जैव", "प्रक्रम", "श्वसन", "पोषण", "जनन", "आनुवंशिक", "गुणसूत्र", "न्यूरॉन", "हार्मोन",
                "कोशिका", "विकास", "पर्यावरण", "रक्त", "हृदय", "नेफ्रॉन"],
}


def detect_science_subject(text):
    low = str(text)
    best, score = None, 0
    for sub, kws in SCIENCE_KEYWORDS.items():
        s = sum(1 for k in kws if k in low)
        if s > score:
            score, best = s, sub
    return best if score >= 2 else None


def split_science():
    """Split science bank into physics/chemistry/biology."""
    m = load_module("science", SOURCES["science"])
    buckets = {"physics": [], "chemistry": [], "biology": []}
    c = Counter("sc")
    chapter_idx = {k: 0 for k in buckets}
    current = None

    for section in m.SECTIONS:
        title = section[0]
        t = title
        if ("रसायन" in t or "chemistry" in t.lower()):
            current = "chemistry"
        elif ("भौतिक" in t or "physics" in t.lower()):
            current = "physics"
        elif ("जीव" in t or "biology" in t.lower()):
            current = "biology"
        else:
            current = None  # generic section -> detect per question
        seq = section[1]
        prev_q = prev_type = prev_opts = None
        for typ, txt in seq:
            txt = str(txt)
            if typ == 'S':
                continue
            if typ == 'Q':
                prev_q, prev_type, prev_opts = txt, 'Q', None
            elif typ == 'MCQ':
                stem, opts = extract_mcq_parts(txt)
                prev_q, prev_type, prev_opts = stem, 'MCQ', opts
            elif typ == 'A':
                sub = current if current else detect_science_subject(prev_q)
                if sub is None:
                    sub = detect_science_subject(txt)
                if sub is None:
                    continue
                chapter_list = SCIENCE_CHAPTERS[sub]
                ch = chapter_list[chapter_idx[sub] % len(chapter_list)]
                chapter_idx[sub] += 1
                if prev_type == 'MCQ' and prev_q:
                    ansidx, ansval = parse_mcq_answer(txt)
                    buckets[sub].append(to_mcq_q(ch, prev_q, prev_opts, ansidx, ansval, c.nid()))
                    prev_q = None
                elif prev_type == 'Q' and prev_q:
                    buckets[sub].append(to_write_q(ch, prev_q, txt, c.nid()))
                    prev_q = None
    return buckets


# ---------------- Expansion to 300+ ----------------
def fact_bank(subject):
    return FILLERS.get(subject, [])


def short_tag(ch):
    """Clean a chapter name for use inside generated question text."""
    s = str(ch)
    s = re.sub(r'^अध्याय\s*\d+\s*[:：]\s*', '', s)          # "अध्याय 1: " prefix
    s = re.sub(r'\s*\([^)]*[A-Za-z][^)]*\)\s*$', '', s)     # trailing "(English ...)"
    s = re.sub(r'\s*-\s*\d+\s*अंक\s*$', '', s)              # "- 3 अंक"
    s = re.sub(r'\s*\(\s*\d+\s*अंक\s*\)\s*$', '', s)        # "(2 अंक)"
    s = re.sub(r'\s*-\s*\d+\s*प्रश्न\s*$', '', s)           # "- 30 प्रश्न"
    s = re.sub(r'\s*\(\s*\d+\s*प्रश्न\s*\)\s*$', '', s)     # "(25 प्रश्न)"
    s = re.sub(r'\(MCQ\)', '', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


# Map each subject's real chapter names (by keyword, first match wins,
# longest/specific first) to a topic group name from TOPIC_BANK.
CHAPTER_GROUPS = {
    "hindi": [
        ("क्षितिज", "क्षितिज"), ("कृतिका", "कृतिका"), ("स्पर्श", "स्पर्श"),
        ("संचयन", "संचयन"), ("व्याकरण", "व्याकरण"),
    ],
    "english": [
        ("for anne gregory", "First Flight Poetry"), ("custard", "First Flight Poetry"),
        ("fog", "First Flight Poetry"), ("the trees", "First Flight Poetry"),
        ("animals", "First Flight Poetry"), ("amanda", "First Flight Poetry"),
        ("the ball poem", "First Flight Poetry"), ("how to tell wild animals", "First Flight Poetry"),
        ("a tiger in the zoo", "First Flight Poetry"), ("fire and ice", "First Flight Poetry"),
        ("dust of snow", "First Flight Poetry"),
        ("the proposal", "First Flight Prose"), ("sermon", "First Flight Prose"),
        ("madam rides", "First Flight Prose"), ("mijbil", "First Flight Prose"),
        ("glimpses", "First Flight Prose"), ("hundred dresses", "First Flight Prose"),
        ("diary of anne", "First Flight Prose"), ("two stories", "First Flight Prose"),
        ("nelson mandela", "First Flight Prose"), ("a letter to god", "First Flight Prose"),
        ("book that saved", "Footprints"), ("bholi", "Footprints"),
        ("hack driver", "Footprints"), ("necklace", "Footprints"),
        ("making of a scientist", "Footprints"), ("footprints", "Footprints"),
        ("question of trust", "Footprints"), ("midnight visitor", "Footprints"),
        ("thief's story", "Footprints"), ("triumph of surgery", "Footprints"),
        ("first flight", "First Flight Prose"), ("grammar", "Grammar"),
    ],
    "maths": [
        ("वास्तविक संख्याएँ", "संख्याएँ"), ("बहुपद", "बीजगणित"),
        ("रैखिक समीकरण", "बीजगणित"), ("द्विघात समीकरण", "बीजगणित"),
        ("समांतर श्रेढ़ी", "बीजगणित"), ("त्रिकोणमिति के कुछ अनुप्रयोग", "त्रिकोणमिति"),
        ("त्रिकोणमिति का परिचय", "त्रिकोणमिति"), ("त्रिकोणमिति", "त्रिकोणमिति"),
        ("वृत्तों से संबंधित क्षेत्रफल", "क्षेत्रमिति"), ("पृष्ठीय क्षेत्रफल और आयतन", "क्षेत्रमिति"),
        ("वृत्त", "ज्यामिति"), ("त्रिभुज", "ज्यामिति"), ("निर्देशांक ज्यामिति", "ज्यामिति"),
        ("ज्यामिति", "ज्यामिति"), ("सांख्यिकी", "सांख्यिकी"), ("प्रायिकता", "प्रायिकता"),
        ("बीजगणित", "बीजगणित"), ("क्षेत्रमिति", "क्षेत्रमिति"),
    ],
    "physics": [
        ("विद्युत धारा का चुंबकीय प्रभाव", "चुंबकीय प्रभाव"),
        ("मानव नेत्र एवं रंगीन संसार", "मानव नेत्र"),
        ("प्रकाश - परावर्तन एवं अपवर्तन", "प्रकाश"),
        ("ऊर्जा के स्रोत", "ऊर्जा के स्रोत"), ("विद्युत", "विद्युत"),
        ("चुंबकीय प्रभाव", "चुंबकीय प्रभाव"), ("प्रकाश", "प्रकाश"),
        ("नेत्र", "मानव नेत्र"), ("ऊर्जा", "ऊर्जा के स्रोत"),
    ],
    "chemistry": [
        ("तत्वों का आवर्त वर्गीकरण", "तत्वों का आवर्त वर्गीकरण"),
        ("रासायनिक अभिक्रियाएँ और समीकरण", "रासायनिक अभिक्रियाएँ"),
        ("रासायनिक अभिक्रियाएँ", "रासायनिक अभिक्रियाएँ"),
        ("अम्ल, क्षारक एवं लवण", "अम्ल क्षारक लवण"), ("अम्ल क्षारक लवण", "अम्ल क्षारक लवण"),
        ("धातु और अधातु", "धातु अधातु"), ("धातु अधातु", "धातु अधातु"),
        ("कार्बन और उसके यौगिक", "कार्बन यौगिक"), ("कार्बन यौगिक", "कार्बन यौगिक"),
        ("आवर्त", "तत्वों का आवर्त वर्गीकरण"),
    ],
    "biology": [
        ("हमारा पर्यावरण", "हमारा पर्यावरण"), ("पर्यावरण", "हमारा पर्यावरण"),
        ("नियंत्रण एवं समन्वय", "नियंत्रण समन्वय"), ("नियंत्रण समन्वय", "नियंत्रण समन्वय"),
        ("जीव जनन कैसे करते हैं", "जनन"), ("जनन", "जनन"),
        ("आनुवंशिकता एवं जैव विकास", "आनुवंशिकता"), ("आनुवंशिकता", "आनुवंशिकता"),
        ("जैव प्रक्रम", "जैव प्रक्रम"),
    ],
    "history": [
        ("भूमंडलीकृत", "भूमंडलीकृत विश्व"),
        ("यूरोप में राष्ट्रवाद", "राष्ट्रवाद"), ("भारत में राष्ट्रवाद", "राष्ट्रवाद"),
        ("राष्ट्रवाद", "राष्ट्रवाद"),
        ("मुद्रण संस्कृति", "मुद्रण संस्कृति"), ("मुद्रण", "मुद्रण संस्कृति"),
        ("औद्योगीकरण", "औद्योगीकरण"),
    ],
    "geography": [
        ("संसाधन एवं विकास", "संसाधन"), ("संसाधन", "संसाधन"),
        ("वन और वन्य जीव", "वन"), ("वन", "वन"),
        ("जल संसाधन", "जल संसाधन"), ("जल", "जल संसाधन"),
        ("कृषि", "कृषि"), ("खनिज तथा ऊर्जा", "खनिज"), ("खनिज", "खनिज"),
        ("विनिर्माण उद्योग", "उद्योग"), ("उद्योग", "उद्योग"),
        ("जीवन रेखाएँ", "परिवहन"), ("परिवहन", "परिवहन"),
    ],
    "civics": [
        ("सत्ता की साझेदारी", "सत्ता साझेदारी"), ("सत्ता साझेदारी", "सत्ता साझेदारी"),
        ("संघवाद", "संघवाद"),
        ("लोकतंत्र और विविधता", "विविधता"), ("जाति, धर्म", "विविधता"),
        ("जन-संघर्ष", "संघर्ष"),
        ("राजनीतिक दल", "राजनीतिक दल"),
        ("लोकतंत्र के परिणाम", "लोकतंत्र"), ("लोकतंत्र की चुनौतियाँ", "चुनौतियाँ"),
        ("लोकतंत्र", "लोकतंत्र"),
    ],
    "economics": [
        ("उपभोक्ता अधिकार", "उपभोक्ता अधिकार"),
        ("क्षेत्रक", "अर्थव्यवस्था"), ("अर्थव्यवस्था", "अर्थव्यवस्था"),
        ("वैश्वीकरण", "वैश्वीकरण"), ("मुद्रा और साख", "मुद्रा और साख"),
        ("मुद्रा", "मुद्रा और साख"), ("विकास", "विकास"),
    ],
}


def group_chapter(subject, short):
    for kw, group in CHAPTER_GROUPS.get(subject, []):
        if kw in short:
            return group
    return None


def generate_write_questions(subject, chapters, need, existing_questions):
    """Generate `need` additional write-type questions deterministically using
    subject topic banks combined with question templates (topics × templates).
    The chapter tag is cleaned and the topics are chosen to match the chapter.
    """
    out = []
    existing_texts = set(q["q"] for q in existing_questions)
    topics = TOPIC_BANK.get(subject, {})
    templates = WRITE_TEMPLATES.get(subject, WRITE_TEMPLATES["default"])
    generic = topics.get("*", [])
    gen_c = Counter("ztop")

    def try_add(qtext, answer):
        if qtext in existing_texts:
            return False
        existing_texts.add(qtext)
        out.append(to_write_q(answer.get("_ch", "मुख्य"), qtext, answer["ans"], gen_c.nid()))
        return True

    for ch in chapters:
        short = short_tag(ch) or "मुख्य"
        group = group_chapter(subject, short)
        ch_topics = (topics.get(group, []) if group else []) + generic
        if not ch_topics:
            continue
        for top in ch_topics:
            for tpl in templates:
                qtext = tpl["q"].format(t=top) + " (" + short + ")"
                answer = tpl["ans"].format(t=top, ch=short)
                qtext = qtext.replace("  ", " ")
                if try_add(qtext, {"ans": answer, "_ch": short}):
                    if len(out) >= need:
                        return out
    return out


# Subject topic banks: group -> list of topic nouns used in write templates.
# "*" topics are subject-neutral concepts that read naturally with any chapter.
TOPIC_BANK = {
    "hindi": {
        "*": ["शीर्षक की सार्थकता", "मुख्य भाव", "संदेश", "पात्र-चरित्र", "भाषा शैली",
              "कथानक", "भाव-व्याख्या", "प्रकृति-चित्रण", "कहानी का उद्देश्य", "रचनाकार का परिचय"],
        "व्याकरण": ["संज्ञा", "सर्वनाम", "विशेषण", "क्रिया", "काल", "वाच्य", "कारक", "अलंकार",
                    "रस", "समास", "उपसर्ग", "प्रत्यय", "संधि", "विराम चिह्न", "पर्यायवाची शब्द",
                    "विलोम शब्द", "मुहावरे", "लोकोक्तियाँ"],
        "क्षितिज": ["गद्य", "पद्य", "कहानी", "निबंध"],
        "कृतिका": ["मातृ प्रेम", "यात्रा वर्णन", "स्वतंत्रता"],
        "स्पर्श": ["गद्य", "पद्य", "कहानी", "यात्रा वृत्तांत"],
        "संचयन": ["संस्मरण", "जीवन-परिचय", "प्रेरक घटना"],
    },
    "english": {
        "*": ["theme", "character", "moral", "message", "plot", "setting", "title",
              "narrator", "figure of speech", "summary"],
        "First Flight Prose": ["Lencho", "faith", "Nelson Mandela", "the young seagull",
                               "Anne Frank", "Valli", "the baker", "Mijbil", "Kisa Gotami", "the proposal"],
        "First Flight Poetry": ["Dust of Snow", "Fire and Ice", "the tiger", "the ball",
                                "Amanda", "the animals", "the trees", "the fog", "Custard", "Anne Gregory"],
        "Footprints": ["Griffin", "Tricki", "the thief", "the midnight visitor", "trust",
                       "the hack driver", "Bholi", "the scientist", "the necklace", "the book"],
        "Grammar": ["tenses", "articles", "modals", "voice", "reported speech", "prepositions", "narration"],
    },
    "maths": {
        "*": ["सूत्र", "आलेख", "अनुपात", "औसत", "मात्रक", "गुणनखंड"],
        "संख्याएँ": ["अभाज्य संख्या", "परिमेय संख्या", "अपरिमेय संख्या", "म.स.", "ल.स."],
        "बीजगणित": ["बहुपद", "द्विघात समीकरण", "समांतर श्रेढ़ी", "रैखिक समीकरण", "शून्यक"],
        "ज्यामिति": ["त्रिभुज", "वृत्त", "स्पर्श रेखा", "समरूपता", "निर्देशांक"],
        "त्रिकोणमिति": ["sin θ", "cos θ", "tan θ", "ऊँचाई-दूरी"],
        "क्षेत्रमिति": ["बेलन", "गोला", "शंकु", "चाप", "त्रिज्यखंड"],
        "सांख्यिकी": ["माध्य", "माध्यक", "बहुलक"],
        "प्रायिकता": ["घटना", "प्रायिकता"],
    },
    "physics": {
        "*": ["वेग", "गति", "बल", "पदार्थ", "ऊर्जा", "मात्रक", "मापन", "परिमाण"],
        "विद्युत": ["ओम का नियम", "प्रतिरोध", "विभवांतर", "विद्युत धारा", "विद्युत शक्ति"],
        "मानव नेत्र": ["रेटिना", "निकट दृष्टि", "दीर्घ दृष्टि", "निकट बिंदु", "दूर बिंदु"],
        "प्रकाश": ["परावर्तन", "अपवर्तन", "दर्पण", "लेंस", "आवर्धन"],
        "चुंबकीय प्रभाव": ["विद्युत मोटर", "जनरेटर", "विद्युत चुंबक", "प्रेरण"],
        "ऊर्जा के स्रोत": ["सौर ऊर्जा", "नाभिकीय ऊर्जा", "पवन ऊर्जा", "जल विद्युत", "जैव ईंधन"],
    },
    "chemistry": {
        "*": ["परमाणु", "अणु", "तत्व", "यौगिक", "आयन"],
        "रासायनिक अभिक्रियाएँ": ["संयोजन अभिक्रिया", "अपघटन अभिक्रिया", "विस्थापन अभिक्रिया", "ऑक्सीकरण", "अपचयन"],
        "अम्ल क्षारक लवण": ["pH", "उदासीनीकरण", "लिटमस", "एंटासिड"],
        "धातु अधातु": ["धातु", "अधातु", "निष्कर्षण", "संक्षारण"],
        "कार्बन यौगिक": ["कैटिनेशन", "कार्यात्मक समूह", "साबुन"],
        "तत्वों का आवर्त वर्गीकरण": ["आवर्त सारणी", "परमाणु क्रमांक", "प्रवृत्ति", "समूह", "आवर्त"],
    },
    "biology": {
        "*": ["कोशिका", "ऊतक", "अंग", "पोषण", "वृद्धि"],
        "जैव प्रक्रम": ["प्रकाश संश्लेषण", "श्वसन", "परिवहन", "उत्सर्जन"],
        "नियंत्रण समन्वय": ["न्यूरॉन", "हार्मोन", "अनुक्रिया"],
        "जनन": ["अलैंगिक जनन", "लैंगिक जनन", "परागण"],
        "आनुवंशिकता": ["जीन", "DNA", "गुणसूत्र", "मेंडल नियम"],
        "हमारा पर्यावरण": ["पारिस्थितिकी तंत्र", "खाद्य श्रृंखला", "ओजोन परत", "जैव विविधता"],
    },
    "history": {
        "*": ["अभिलेख", "ग्रंथ", "समाज", "सभ्यता", "अर्थव्यवस्था", "इतिहास"],
        "राष्ट्रवाद": ["राष्ट्रवाद", "फ्रांस की क्रांति", "नेपोलियन", "सत्याग्रह",
                       "असहयोग आंदोलन", "दांडी मार्च", "भारत छोड़ो आंदोलन"],
        "भूमंडलीकृत विश्व": ["वैश्विक अर्थव्यवस्था", "जनसंख्या विस्थापन", "व्यापारिक मार्ग", "उपनिवेशवाद"],
        "औद्योगीकरण": ["औद्योगिक क्रांति", "सूती वस्त्र", "कारखाने"],
        "मुद्रण संस्कृति": ["छापाखाना", "पुस्तकें", "साक्षरता"],
    },
    "geography": {
        "*": ["संसाधन", "जनसंख्या", "जलवायु", "पर्यावरण", "प्रदूषण"],
        "संसाधन": ["जलोढ़ मिट्टी", "काली मिट्टी", "मृदा संरक्षण"],
        "वन": ["वन", "वन्य जीव", "जैव विविधता", "संरक्षण"],
        "जल संसाधन": ["जल", "सिंचाई", "बहुउद्देशीय परियोजना"],
        "कृषि": ["खरीफ", "रबी", "जायद", "धान", "गेहूँ"],
        "खनिज": ["कोयला", "लौह अयस्क", "बॉक्साइट", "अयस्क"],
        "उद्योग": ["सूती वस्त्र", "जूट", "इस्पात"],
        "परिवहन": ["सड़क", "रेल", "जल परिवहन", "वायु परिवहन"],
    },
    "civics": {
        "*": ["सरकार", "कानून", "नागरिक", "अधिकार", "लोकतंत्र"],
        "सत्ता साझेदारी": ["बेल्जियम मॉडल", "श्रीलंका", "विकेंद्रीकरण"],
        "संघवाद": ["संघ सूची", "राज्य सूची", "समवर्ती सूची", "पंचायती राज"],
        "विविधता": ["विविधता", "भाषाई विविधता", "धर्म", "लैंगिक समानता"],
        "संघर्ष": ["आंदोलन", "संघर्ष", "प्रतिरोध"],
        "राजनीतिक दल": ["राष्ट्रीय दल", "क्षेत्रीय दल", "दल बदल नियम"],
        "लोकतंत्र": ["जवाबदेही", "नागरिक अधिकार", "चुनाव"],
        "चुनौतियाँ": ["भ्रष्टाचार", "समानता", "विकास"],
    },
    "economics": {
        "*": ["आय", "बचत", "बाजार", "कीमत", "रोजगार", "मुद्रा"],
        "विकास": ["प्रति व्यक्ति आय", "HDI", "साक्षरता"],
        "अर्थव्यवस्था": ["प्राथमिक क्षेत्रक", "द्वितीयक क्षेत्रक", "तृतीयक क्षेत्रक", "GDP"],
        "मुद्रा और साख": ["मुद्रा", "बैंक", "RBI", "ऋण"],
        "वैश्वीकरण": ["MNC", "विदेशी निवेश", "WTO"],
        "उपभोक्ता अधिकार": ["उपभोक्ता अधिकार", "AGMARK", "शिकायत"],
    },
}


WRITE_TEMPLATES = {
    "default": [
        {"q": "{t} किसे कहते हैं?", "ans": "{t} की स्पष्ट परिभाषा लिखें; {ch} अध्याय से संबंधित उदाहरण देकर समझाएँ।"},
        {"q": "{t} की परिभाषा और महत्व लिखिए।", "ans": "{t} की परिभाषा के साथ उसका महत्व {ch} अध्याय के संदर्भ में लिखें।"},
        {"q": "{t} को उदाहरण सहित समझाइए।", "ans": "{t} को एक स्पष्ट उदाहरण के साथ समझाएँ; यह {ch} अध्याय का महत्वपूर्ण भाग है।"},
        {"q": "{t} के प्रमुख बिंदु या गुण लिखिए।", "ans": "{t} के मुख्य बिंदुओं को क्रमबद्ध रूप में लिखें, जैसा {ch} अध्याय में वर्णित है।"},
        {"q": "{t} पर एक संक्षिप्त टिप्पणी लिखिए।", "ans": "{t} पर टिप्पणी में मूल अवधारणा, कारण और प्रभाव को संक्षेप में लिखें, जैसा {ch} में है।"},
        {"q": "{t} का महत्व बताइए।", "ans": "{t} का महत्व {ch} अध्याय के संदर्भ में स्पष्ट करें; सही परिभाषा के साथ एक उदाहरण दें।"},
        {"q": "{t} के अंतर्गत मुख्य बिंदु क्या-क्या हैं, बताइए।", "ans": "{t} से संबंधित मुख्य बिंदुओं को क्रमबद्ध सूची में लिखें, जैसा {ch} अध्याय में है।"},
    ],
    "english": [
        {"q": "Define {t}.", "ans": "Define {t} clearly and give an example relevant to the chapter '{ch}'."},
        {"q": "Explain {t} with an example.", "ans": "Explain {t} with a suitable example drawn from the chapter '{ch}'."},
        {"q": "Write a short note on {t}.", "ans": "Write the definition, importance and one example of {t} in a short note related to '{ch}'."},
        {"q": "What is the importance of {t}?", "ans": "{t} is important because it helps us understand the ideas of the chapter '{ch}'."},
        {"q": "Give two points about {t}.", "ans": "Mention two key facts about {t} from the chapter '{ch}'."},
    ],
}


def build_subject(subject, chapters, base_items):
    """Combine base + fact bank MCQs + generated write questions to reach MIN."""
    all_chapters = list(dict.fromkeys([i["chapter"] for i in base_items] + chapters))
    if not all_chapters:
        all_chapters = chapter_defaults(subject)
    out = list(base_items)
    existing = set(i["q"] for i in out)

    # add fact bank - each fact becomes an MCQ AND a write question (if applicable)
    fb = fact_bank(subject)
    fbc = Counter(subject + "-fb")
    wc = Counter(subject + "-fw")
    extra_write = []
    for f in fb:
        ch = f.get("chapter") or all_chapters[0]
        if f["q"] not in existing:
            existing.add(f["q"])
            out.append(to_mcq_q(ch, f["q"], f["opts"], f["answer"], f["opts"][f["answer"]], fbc.nid()))
        wq = f.get("wq")
        wa = f.get("wa")
        if wq and wa:
            key = wq
            if key not in existing:
                existing.add(key)
                extra_write.append(to_write_q(ch, wq, wa, wc.nid()))

    # generate write questions to reach minimum
    need = MIN_QUESTIONS - len(out)
    if need > 0:
        gen = generate_write_questions(subject, all_chapters, need, out)
        out.extend(gen)
        if len(out) < MIN_QUESTIONS:
            for item in extra_write:
                if len(out) >= MIN_QUESTIONS:
                    break
                item["id"] = wc.nid()
                out.append(item)

    return all_chapters, out


def chapter_defaults(subject):
    return {
        "hindi": ["क्षितिज", "कृतिका", "स्पर्श", "संचयन", "व्याकरण"],
        "english": ["First Flight", "Footprints without Feet", "Grammar"],
        "maths": ["बीजगणित", "त्रिकोणमिति", "क्षेत्रमिति", "ज्यामिति", "सांख्यिकी", "प्रायिकता"],
        "physics": ["विद्युत", "मानव नेत्र", "प्रकाश", "चुंबकीय प्रभाव", "ऊर्जा के स्रोत"],
        "chemistry": ["रासायनिक अभिक्रियाएँ", "अम्ल क्षारक लवण", "धातु अधातु", "कार्बन यौगिक", "तत्वों का आवर्त वर्गीकरण"],
        "biology": ["जैव प्रक्रम", "नियंत्रण समन्वय", "जनन", "आनुवंशिकता", "हमारा पर्यावरण"],
        "history": ["राष्ट्रवाद", "भूमंडलीकृत विश्व", "औद्योगीकरण", "मुद्रण संस्कृति"],
        "geography": ["संसाधन", "वन", "जल संसाधन", "कृषि", "खनिज", "उद्योग", "परिवहन"],
        "civics": ["सत्ता साझेदारी", "संघवाद", "विविधता", "राजनीतिक दल", "लोकतंत्र"],
        "economics": ["विकास", "अर्थव्यवस्था", "मुद्रा और साख", "वैश्वीकरण", "उपभोक्ता अधिकार"],
    }.get(subject, ["मुख्य"])


def write_json(subject, chapters, questions):
    data = {"subject": SUBJECTS_META[subject]["name"], "chapters": chapters,
            "questions": questions}
    path = os.path.join(OUT, subject + ".json")
    with io.open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)
    print(f"{subject}: {len(questions)} questions, {len(chapters)} chapters -> {path}")


def main():
    fixed = ["hindi", "english", "maths", "history", "geography", "civics", "economics"]
    for sub in fixed:
        base = parse_bank(SOURCES[sub], sub)
        chapters, out = build_subject(sub, [], base)
        write_json(sub, chapters, out)

    buckets = split_science()
    for part in ["physics", "chemistry", "biology"]:
        base = buckets[part]
        chapters, out = build_subject(part, [], base)
        write_json(part, chapters, out)


if __name__ == "__main__":
    main()