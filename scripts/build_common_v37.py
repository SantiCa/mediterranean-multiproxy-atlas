"""Append six published pollen-based seasonal climate sequences."""
import argparse

import build_common_v19 as pipeline
from build_common_v36 import calendar_bp

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v36.json'
CONTRACT = ROOT / 'scripts/importers/common_v37_sources.json'
RAW = ROOT / 'data/interim/common_v37'


def build(fetch=False):
    pipeline.curator.FAMILIES['pollen_climate'] = 'Polen'
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=37, release_date='2026-11-18',
                          age_rule=calendar_bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
