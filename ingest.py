
from __future__ import annotations
import os, json, argparse, pathlib, tqdm
from .utils import load_any, norm_item

def ingest_folder(input_dir: str, out_jsonl: str) -> None:
    input_dir = os.path.abspath(input_dir)
    items = 0
    with open(out_jsonl, 'w', encoding='utf-8') as out:
        for root, _, files in os.walk(input_dir):
            for fn in files:
                p = os.path.join(root, fn)
                if not any(fn.lower().endswith(ext) for ext in ('.md','.txt','.json','.yaml','.yml','.py','.ts','.js','.pdf')):
                    continue
                txt = load_any(p)
                if not txt.strip():
                    continue
                item = norm_item(p, txt)
                out.write(json.dumps(item, ensure_ascii=False) + "\n")
                items += 1
    print(f"[ingest] wrote {items} items to {out_jsonl}")

if __name__ == '__main__':
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True)
    ap.add_argument('--out', required=True)
    args = ap.parse_args()
    os.makedirs(os.path.dirname(args.out), exist_ok=True)
    ingest_folder(args.input, args.out)
