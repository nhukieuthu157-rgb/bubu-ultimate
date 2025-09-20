
from __future__ import annotations
import json, argparse, os
from typing import List, Dict, Any
from collections import defaultdict

def synthesize(items_path: str, out_dir: str, project_name: str, agent_name: str, lang: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    items = [json.loads(l) for l in open(items_path, 'r', encoding='utf-8')]
    # bucket by topic
    buckets = defaultdict(list)
    for it in items:
        for t in it.get('topics', ['general']):
            buckets[t].append(it)
    intents = []
    for t, arr in buckets.items():
        seen = set()
        for it in arr:
            for intent in it.get('intents', []):
                k = json.dumps(intent, sort_keys=True)
                if k not in seen:
                    seen.add(k); intents.append({**intent, 'topic': t})
    # save intents
    intents_path = os.path.join(out_dir, 'intents.json')
    with open(intents_path, 'w', encoding='utf-8') as f:
        json.dump({'project': project_name, 'agent': agent_name, 'lang': lang, 'intents': intents}, f, ensure_ascii=False, indent=2)
    return intents_path

if __name__ == '__main__':
    import argparse, os
    ap = argparse.ArgumentParser()
    ap.add_argument('--items', required=True)
    ap.add_argument('--out', required=True)
    ap.add_argument('--project-name', default='it-project')
    ap.add_argument('--agent', default='GermanyAgent')
    ap.add_argument('--lang', default='th')
    args = ap.parse_args()
    os.makedirs(args.out, exist_ok=True)
    p = synthesize(args.items, args.out, args.project_name, args.agent, args.lang)
    print('[synthesize] intents at', p)
