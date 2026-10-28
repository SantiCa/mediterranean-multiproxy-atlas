"""Mirror Sites source into the scientific GitHub checkout, excluding local state."""
import argparse
from pathlib import Path
import shutil

ROOT=Path(__file__).resolve().parents[1]
IGNORED={'.git','node_modules','dist','.sites-runtime','.vinext','.wrangler','.next','outputs','__pycache__'}

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('site_dir',type=Path);args=p.parse_args()
    source=args.site_dir.resolve();target=ROOT/'app/atlas-web'
    if not (source/'.openai/hosting.json').is_file():raise RuntimeError('Not a configured Sites source checkout')
    count=0
    for file in source.rglob('*'):
        relative=file.relative_to(source)
        if not file.is_file() or any(part in IGNORED for part in relative.parts):continue
        if file.name.startswith(('.env','.dev.vars')) or file.suffix=='.tsbuildinfo':continue
        output=target/relative;output.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(file,output);count+=1
    print(f'Mirrored {count} source files into {target}; local runtime and credentials excluded.')
