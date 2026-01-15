import pathlib
import json
import re
import os
import nltk
from urllib.parse import urlparse

line_patterns_general = [
    
    re.compile(r'(?im)^\s*By\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+,\s*BBC\s+News\.?\s*$'),
    
    re.compile(r'(?im)^\s*(?:copyright\s*)?©\s*\d{4}\s*[\w\s\.-]+\.?\s*all\s+rights\s+reserved\.?\s*$'),
    
    re.compile(r'(?im)^\s*This text may not be in its final form and may be updated or revised\.?\s*$'),
    
    re.compile(r'(?im)^\s*See full coverage on BBC News\.?\s*$'),
    re.compile(r'(?im)^\s*The BBC is not responsible for the content of external sites\.?\s*$'),
    re.compile(r'(?im)^\s*This article was originally written in German\.?\s*$'),
    re.compile(r'(?im)^\s*Watch tonight[’\'`]s PBS NewsHour for more coverage\.?\s*$'),
    re.compile(r'(?im)^\s*(?:Join our mailing list|Subscribe for more stories|Click here to read more|Share this article)\.?\s*$'),
    
    re.compile(r'(?im)^\s*Published\s+On\b.*$'),
    re.compile(r'(?im)^\s*By\s+Al\s+Jazeera\s+Staff\s*$'),
    re.compile(r'(?im)^\s*Source:\s*Al\s+Jazeera\s*$'),
    re.compile(r'(?im)^\s*Follow\b.*$'),
    re.compile(r'(?im)^\s*Share\s*$'),
    re.compile(r'(?im)^\s*Save\s*$'),
    re.compile(r'(?im)^\s*READ\s+MORE[:：]?\s*$'),
    re.compile(r'(?im)^\s*Leave\s+your\s+feedback\s*$'),
    re.compile(r'(?im)^\s*Thank\s+you\.?\s*$'),
    re.compile(r'(?im)^\s*Please\s+check\s+your\s+inbox\s+to\s+confirm\.?\s*$'),
    re.compile(r'(?im)^\s*All\s+Rights\s+Reserved\.?\s*$'),
    re.compile(r'(?im)^\s*©\s*\d{4}.*$'),
    re.compile(r'(?im)^\s*Subscribe\b.*$'),
    re.compile(r'(?im)^\s*Learn\s+more\s*$'),
    re.compile(r'(?im)^\s*Sections\s*$'),
    re.compile(r'(?im)^\s*About\s*$'),
    re.compile(r'(?im)^\s*Stay\s+Connected\s*$'),
    re.compile(r'(?im)^Audio\s+on.*may\s+be\s+edited.*$'),
    re.compile(r'(?im)^Transcript\s+text\s+may\s+be\s+revised.*$'),
    re.compile(r'(?im)^Accuracy\s+and\s+availability.*$'),
    re.compile(r'(?im)^Notice:\s*Transcripts?.*lightly\s+edited.*$'),
    re.compile(r'(?im)^\s*Sponsor\s+Message\s*$'),
    re.compile(r'(?im)^\s*hide\s+caption\s*$'),
    re.compile(r'(?im)^Visit\s+our\s+website\s+terms\s+of\s+use.*$'),
    re.compile(r'(?im)^Support\s+for\s+News\s+Hour\s+Provided\s+By.*$'),
    re.compile(r'(?im)^\s*(?:By\s+)?[A-Z][a-z]+\s+[A-Z][a-z]+(?:,\s*[A-Z][a-z]+\s+[A-Z][a-z]+)*\s*$'),
    re.compile(r'(?im)^\s*Watch\s+the\s+Full\s+Episode.*$'),
    re.compile(r'(?im)^©\s*1996\s*-\s*2025\s*NewsHour\s+Productions\s+LLC\..*$'),
    re.compile(r'(?im)^\s*By\s+[A-Z][A-Za-z .,-]*(?:News|Press|Staff|Agency)?\.?\s*$'),
    re.compile(
        r'(?im)^\s*(?:Photo\s+by|Photo\s*[:\-]|Support\s+Provided\s+By[:\-])?\s*'
        r'By\s+'
        r'[A-Z][A-Za-z0-9 .,’\'\-]*(?:Press|News|Staff|Agency|Service|AP|NPR|BBC)?'
        r'\.?\s*$'
    )

]

line_patterns_specific = [
    # AP photo credit
    re.compile(r'(?im)^[^\n]*\((?:AP\s+Photo|AP)\s*/[^)]+\)[^\n]*$'),
    # AP hub link
    re.compile(r'(?im)^\s*AP\s+[A-Z]{2,}:\s*\S+\s*$'),
    # standalone (AP)
    re.compile(r'(?im)^\s*\(AP\)\s*$'),
    # correction lines
    re.compile(r'(?im)^\s*CORRECTION\b.*$'),
    # multiple AP copyright
    re.compile(r'(?im)(?:^\s*(?:copyright\s*)?©?\s*20\d{2}\s*(?:the\s+)?associated\s+press\.?\s*all\s+rights\s+reserved\.?\s*$\s*)+'),
    re.compile(r'(?im)^\s*Become\s+an\s+NPR\s+sponsor\s*$'),
    re.compile(r'(?im).*Avelar\/AP.*$'),
    re.compile(r'(?im)^\s*Lisa\s+Desjardins.*$'),
    re.compile(r'(?im)^\s*Eliot\s+Barnhart.*$'),
    re.compile(r'(?im)^\s*PBS\s+is\s+a\s+501\(c\)\(3\)\s+not-for-profit\s+organization\.?\s*$'),
    re.compile(r'(?im)^\s*By\s+Reuters\s*$'),
    re.compile(r'(?im)^\s*By\s+[A-Z][A-Za-z .,-]+?\s+and\s+Reuters\s*$'),
    re.compile(r'(?im)^\s*By\s+[A-Z][A-Za-z .,-]+?\s+and\s+News\s+Agencies\s*$'),
    re.compile(r'(?im)^\s*Follow\s+Al\s+Jazeera(?:\s+English)?\s*:?\s*$'),
    re.compile(r'(?im)^\s*\(AP\s+Photo.*\)$'),
    re.compile(r'(?im)^\s*(The\s+)?Associated\s+Press\s*$'),
    re.compile(r'(?im)^Stay\s+up\s+to\s+date\s+with\s+the\s+news.*$'),
    re.compile(r'(?im)^\s*By\s+Associated\s+Press\s*$'),
    re.compile(r'(?im)^\s*\(?AP\)?[^\n]*$'),
]

inline_patterns = [
    # first published date
    re.compile(r'(?i)\bfirst\s+published\s+on\s+(?:\d{1,2}\s+\w+\s+\d{4}|\w+\s+\d{1,2},?\s+\d{4})\.?'),

    re.compile(r'(?i)\bedited\s+by\s+[A-Z][\w\s\.-]+[.,]?'),
    re.compile(r'(?i)\breporting\s+by\s+[A-Z][\w\s\.-]+[.,]?'),
    # social media
    re.compile(r'(?i)\bfollow\s+[A-Z][\w\.-]+(?:\s+[A-Z][\w\.-]+)*\s+on\s+[A-Z][\w\s\.-]+[.,]?'),
    # newsletter/newspaper signup
    re.compile(r'(?i)\bsign\s+up\s+for\s+the\s+[A-Z][\w\s\.-]+\s+(?:newsletter|newspaper)[.!]?\s*'),
    # listen to
    re.compile(r'(?i)\blisten\s+to\s+this\s+story\s+on\s+(?:all\s+things\s+considered|morning\s+edition)[.!]?\s*'),
    # inline AP photo credit
    re.compile(r'\s*\(AP\s+Photo/[^)]+\)'),
    re.compile(r'(?i)did\s+not\s+respond\s+to\s+(?:a\s+)?(?:request\s+for\s+)?comment'),
    re.compile(r'(?i)declined\s+to\s+comment'),
    re.compile(r'(?i)asked\s+for\s+comment'),
    re.compile(r'(?i)could\s+not\s+be\s+reached\s+for\s+comment'),
    re.compile(r'(?i)not\s+immediately\s+available\s+for\s+comment'),
    re.compile(r'(?i)according\s+to\s+the\s+statement'),
    re.compile(r'(?i)in\s+an\s+emailed\s+statement'),
    re.compile(r'(?i)as\s+of\s+press\s+time'),
]

# less aggressive to avoid over deletion
fallback_line_patterns = [
    re.compile(r'(?im)^\s*(?:copyright\s*)?©\s*\d{4}.*all\s+rights\s+reserved\.?\s*$'),
    re.compile(r'(?im)^\s*CORRECTION\b.*$'),
    re.compile(r'(?im)^[^\n]*\((?:AP\s+Photo|AP)\s*/[^)]+\)[^\n]*$'),
    re.compile(r'(?im)^\s*AP\s+[A-Z]{2,}:\s*\S+\s*$'),
    re.compile(r'(?im)^\s*\(AP\)\s*$'),
]
fallback_inline_patterns = [
    re.compile(r'\s*\(AP\s+Photo/[^)]+\)'),
]

def normalize_whitespace(s: str) -> str:
    s = s.replace('\r\n', '\n').replace('\r', '\n')
    # trim lines and drop empties created by removals
    s = '\n'.join(line for line in (ln.strip() for ln in s.split('\n')) if line)
    # multiple whitespaces to one
    s = re.sub(r'[ \t\u00A0]+', ' ', s)
    return s.strip()

def apply_rules(text: str, line_rules, inline_rules) -> str:
    res = text
    # Apply line-level deletions
    for rx in line_rules:
        res = rx.sub('', res)
    # Apply inline-safe deletions
    for rx in inline_rules:
        res = rx.sub('', res)
    return normalize_whitespace(res)

def clean_article(data: str, min_ratio: float = 0.4, min_chars: int = 200) -> str:
    """ remove boilerplate while avoiding over-deletion. Use less aggressive if result is too short """
    original = data or ""
    if not original.strip():
        return original

    cleaned = apply_rules(
        original,
        line_rules=line_patterns_specific + line_patterns_specific,
        inline_rules=inline_patterns
    )

    # if deleted too much, retry with less aggressive rules
    if (len(cleaned) < min_chars) or (len(cleaned) < min_ratio * len(original)):
        cleaned_fallback = apply_rules(
            original,
            line_rules=fallback_line_patterns,
            inline_rules=fallback_inline_patterns
        )
        # if still too short, return normalized original
        if (len(cleaned_fallback) < min_chars) or (len(cleaned_fallback) < min_ratio * len(original)):
            return normalize_whitespace(original)
        return cleaned_fallback

    return cleaned

def clean_img_srcs(url, srcs):
    domain = re.search(r'^(?:https?:\/\/)?(?:www\.)?([^\/:?#]+)',url).group(1)

    seen = set()
    unique_sources = []

    srcs = [s for s in srcs if not (
        "promo" in s or 
        ".svg" in s or 
        "placeholder" in s or
        s.startswith("data:image")
    )]
    for src in srcs:
        parsed = urlparse(src)
        filename = parsed.path.split("/")[-1]
        if filename not in seen:
            seen.add(filename)
            unique_sources.append(src)

    if "aljazeera" in domain:
        return list(map(lambda src: f"https://{domain}/{src}", unique_sources))
    elif "apnews" in domain:
        return [src for src in unique_sources if ".png" not in src]
    else:
        return unique_sources

def clean_title(title):
    """ clean up titles of articles for frontend UI """
    reg = re.compile(
        r'(?i)\s*(\|\s*(PBS News|Al Jazeera|AP News)'
        r'|:\s*NPR'
        r'|[-–]\s*DW(\s*[-–]\s*\d{1,2}/\d{1,2}/\d{4})?)\s*$'
    )
    title = title.replace("—", "–").replace("-", "–")

    return normalize_whitespace(reg.sub('', title))


def append_to_json_array(path, obj):
    """ write all article json data for debugging purposes """
    p = pathlib.Path(path)
    if p.exists() and p.stat().st_size > 0:
        try:
            data = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            data = []
        if isinstance(data, list):
            data.append(obj)
        else:
            data = [data, obj]  # if file held a single object
    else:
        data = [obj]
    p.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")

def add_to_json_file(path, key, val):
    p = pathlib.Path(path)
    if p.exists() and p.stat().st_size > 0:
        try:
            db = json.loads(p.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            db = {}
        db[key] = val
    else:
        db = {key: val}
    p.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")

def extract_dir_data(dir_path):
    """ given a directory get article data in all its files and clean the data """
    result = []
    for file in os.listdir(dir_path):
        filepath = os.path.join(dir_path,file)
        with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
            data = json.load(f)
        # clean article data by replacing newlines with spaces
        data["title"] = clean_title(data["title"])
        data["content"] = clean_article(data["content"])
        data["images"] = clean_img_srcs(data["url"], data["images"])
        result.append(data)
        f.close()
    return result

def split_into_sentences(text):
    try:
        return nltk.sent_tokenize(text)
    except LookupError:
        nltk.download("punkt")
        nltk.download("punkt_tab")
        return nltk.sent_tokenize(text)