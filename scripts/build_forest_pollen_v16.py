"""Append eight reviewed Reading v3 entities to the immutable v15 parent."""
import argparse
import json

import build_forest_pollen_v10 as pipeline

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v15.json'
CONTRACT = ROOT / 'scripts/importers/pollen_v16_sources.json'


def build(fetch=False):
    """Return v16 and its audit; restore absent pinned originals only on request."""
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT, version=16)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true', help='Restore absent pinned Reading originals')
    args = parser.parse_args()
    _, report = build(args.fetch)
    print(json.dumps({key: report[key] for key in ('version', 'counts')}, ensure_ascii=False))


if __name__ == '__main__':
    main()
