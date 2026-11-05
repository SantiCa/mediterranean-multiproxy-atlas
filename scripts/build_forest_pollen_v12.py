"""Append ten reviewed inland Reading v3 entities to the immutable v11 parent."""
import argparse
import json

import build_forest_pollen_v10 as pipeline

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v11.json'
CONTRACT = ROOT / 'scripts/importers/pollen_v12_sources.json'


def build(fetch=False):
    """Return v12 and its source audit; fetch only absent hash-pinned originals."""
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT, version=12)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Restore absent pinned Reading originals')
    args = parser.parse_args()
    _, report = build(args.fetch)
    print(json.dumps({key: report[key] for key in ('version', 'counts')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
