
from __future__ import annotations
import os, json, argparse, time, requests

GITHUB_SEARCH = "https://api.github.com/search/repositories"
GITHUB_CODE = "https://api.github.com/search/code"

def gh_headers():
    tok = os.getenv('GITHUB_TOKEN', '')
    h = {"Accept": "application/vnd.github+json"}
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    return h

def search_repo(q: str, per_page=3):
    r = requests.get(GITHUB_SEARCH, params={"q": q, "per_page": per_page, "sort": "stars", "order": "desc"}, headers=gh_headers(), timeout=20)
    r.raise_for_status()
    return r.json().get('items', [])

def search_code(q: str, per_page=3):
    r = requests.get(GITHUB_CODE, params={"q": q, "per_page": per_page}, headers=gh_headers(), timeout=20)
    r.raise_for_status()
    return r.json().get('items', [])

def run(intents_path: str, out_json: str, limit: int = 3):
    meta = json.load(open(intents_path,'r',encoding='utf-8'))
    intents = meta.get('intents', [])
    results = []
    for it in intents:
        topic = it['topic']; verb = it['verb']; obj = it['object']
        q = f"{verb} {obj} {topic} in:name,description,readme"
        repos = []
        try:
            repos = search_repo(q, per_page=limit)
            time.sleep(0.5)
        except Exception as e:
            repos = []
        # code search — narrower
        code_items = []
        try:
            code_items = search_code(f"{verb} {topic} {obj} language:python", per_page=limit)
            time.sleep(0.5)
        except Exception:
            code_items = []
        results.append({
            "intent": it,
            "repo_matches": [dict(name=r.get('full_name'), html_url=r.get('html_url'), stars=r.get('stargazers_count')) for r in repos],
            "code_matches": [dict(name=c.get('name'), repo=c.get('repository',{}).get('full_name'), html_url=c.get('html_url'), path=c.get('path')) for c in code_items]
        })
    with open(out_json, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print(f"[github_match] wrote {out_json} with {len(results)} intents")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--intents', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--limit', type=int, default=int(os.getenv('GITHUB_SEARCH_LIMIT','3')))
    args = ap.parse_args()
    run(args.intents, args.out, args.limit)
