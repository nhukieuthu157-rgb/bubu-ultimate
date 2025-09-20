
from __future__ import annotations
import os, json, argparse

def export(intents_path: str, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    meta = json.load(open(intents_path,'r',encoding='utf-8'))
    intents = meta.get('intents', [])
    # flatten to lightweight schema
    pack = [{"topic": it['topic'], "verb": it['verb'], "object": it['object']} for it in intents]
    with open(os.path.join(out_dir, 'agent_intents.json'), 'w', encoding='utf-8') as f:
        json.dump(pack, f, ensure_ascii=False, indent=2)
    print('[export] agent pack at', os.path.join(out_dir,'agent_intents.json'))

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--intents', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    export(args.intents, args.out)
