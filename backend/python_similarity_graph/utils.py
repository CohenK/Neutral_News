import pathlib
import json
import re
import os
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
]

line_patterns_ap = [
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
]

inline_patterns = [
    # "first published date"
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
        line_rules=line_patterns_ap + line_patterns_ap,
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

def extract_dir_data(dir_path):
    """ given a directory get article data in all its files and clean the data """
    result = []
    for file in os.listdir(dir_path):
        filepath = os.path.join(dir_path,file)
        with open(filepath, 'r', encoding='utf-8', errors='strict') as f:
            data = json.load(f)
        # clean article data by replacing newlines with spaces
        data["content"] = clean_article(data["content"])
        data["images"] = clean_img_srcs(data["url"], data["images"])
        result.append(data)
        f.close()
    return result