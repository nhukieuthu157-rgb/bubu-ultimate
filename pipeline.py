
from __future__ import annotations
import os, argparse, json
from .ingest import ingest_folder
from .synthesize import synthesize
from .codegen import generate
from .github_match import run as gh_run
from .export_agent import export

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', required=True, help='Folder containing your It data')
    ap.add_argument('--out', required=True, help='Output folder')
    ap.add_argument('--lang', default='th')
    ap.add_argument('--project-name', default='bubu-ultimate')
    ap.add_argument('--agent', default='GermanyAgent')
    ap.add_argument('--no-github', action='store_true')
    args = ap.parse_args()

    os.makedirs(args.out, exist_ok=True)
    items_path = os.path.join(args.out, 'items.jsonl')
    ingest_folder(args.input, items_path)
    intents_path = synthesize(items_path, os.path.join(args.out, 'synth'), args.project_name, args.agent, args.lang)
    generate(intents_path, os.path.join(args.out, 'generated'))
    if not args.no_github:
        gh_run(intents_path, os.path.join(args.out, 'github_matches.json'))
    export(intents_path, os.path.join(args.out, 'IMPORT_FOR_AGENT'))
    print('[pipeline] done.')

if __name__ == '__main__':
    main()
