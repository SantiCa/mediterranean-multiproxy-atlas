"""Add reviewed organic-carbon and nutrient records without changing the v19 schema."""
import argparse
from pathlib import Path

import build_common_v19 as pipeline

ROOT = Path(__file__).resolve().parents[1]
BASE = ROOT / 'data/processed/atlas-v19.json'
CONTRACT = ROOT / 'scripts/importers/common_v20_sources.json'
RAW = ROOT / 'data/interim/carbon_v20'


def build(fetch=False):
    """Return an immutable-parent extension; uncertain calendar units remain held."""
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT, raw_dir=RAW, version=20)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
