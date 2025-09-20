
from __future__ import annotations
import re, os, json, hashlib, pathlib, base64
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Iterable, Optional
import regex
import yaml

def sha1(s: str) -> str:
    return hashlib.sha1(s.encode('utf-8')).hexdigest()

def read_text_maybe(path: str) -> str:
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except Exception:
        return ""

def read_pdf_text(path: str) -> str:
    try:
        from pdfminer.high_level import extract_text
        return extract_text(path) or ""
    except Exception:
        return ""

def load_any(path: str) -> str:
    p = str(path).lower()
    if p.endswith(('.md', '.txt', '.py', '.ts', '.js')):
        return read_text_maybe(path)
    if p.endswith(('.json',)):
        try:
            import json
            return json.dumps(json.load(open(path, 'r', encoding='utf-8')), ensure_ascii=False, indent=2)
        except Exception:
            return read_text_maybe(path)
    if p.endswith(('.yml', '.yaml')):
        try:
            return yaml.safe_dump(yaml.safe_load(open(path, 'r', encoding='utf-8')), allow_unicode=True, sort_keys=False)
        except Exception:
            return read_text_maybe(path)
    if p.endswith('.pdf'):
        return read_pdf_text(path)
    return ""

TOPIC_HINTS = [
    ('travel', r'visa|flight|hotel|hilton|paris|airport|itinerary|navigo|rER|stade de france'),
    ('shortcuts', r'ios shortcut|shortcuts|automation|workflow|url scheme|x-callback'),
    ('meta_ads', r'meta|pixel|capi|conversion api|ad[s ]|campaign|facebook'),
    ('devops', r'ci/cd|docker|kubernetes|helm|terraform|ansible|pipeline|monitoring'),
    ('ml_ai', r'agent|llm|embedding|vector|retrieval|fine[- ]?tune|prompt'),
    ('finance', r'hilton points|visa infinite|uob|enrich|miles|points'),
    ('automotive', r'car|tire|brake|suspension|elontra|tIgUan|acceleration|km/h'),
    ('media', r'photos?|videos?|exif|exiftool|yt-dlp|ffmpeg|nas|beestation|terr[a]?master'),
]

def guess_topics(text: str) -> List[str]:
    ts = []
    lo = text.lower()
    for name, pat in TOPIC_HINTS:
        if regex.search(pat, lo):
            ts.append(name)
    if not ts:
        ts = ['general']
    return ts

def extract_intents(text: str) -> List[Dict[str, Any]]:
    # very lightweight heuristic intent extractor
    intents = []
    for m in regex.finditer(r'(?m)^(?:- |\* |\d+\.\s*)?(create|build|fix|convert|generate|match|search|monitor|remind|translate)\b[: ](.+)$', text, flags=regex.IGNORECASE):
        verb, rest = m.group(1).lower(), m.group(2).strip()
        intents.append({'verb': verb, 'object': rest})
    # also parse "I want to ..." style
    for m in regex.finditer(r'\b(i want to|need to|let's|make it)\b(.+?)(?:\.|\n|$)', text, flags=regex.IGNORECASE):
        intents.append({'verb': 'do', 'object': m.group(2).strip()})
    # dedupe
    seen = set()
    uniq = []
    for it in intents:
        k = json.dumps(it, sort_keys=True)
        if k not in seen:
            seen.add(k); uniq.append(it)
    return uniq

def norm_item(path: str, content: str) -> Dict[str, Any]:
    return {
        'id': sha1(path + '::' + content[:256]),
        'path': str(path),
        'filename': os.path.basename(path),
        'topics': guess_topics(content),
        'size': len(content),
        'intents': extract_intents(content),
        'preview': content[:500]
    }
