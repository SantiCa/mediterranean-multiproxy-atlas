"""Append reviewed Mediterranean isotope and biomarker records."""
import argparse

import build_common_v19 as pipeline
from build_common_v22 import native_bp

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v26.json'
CONTRACT = ROOT / 'scripts/importers/common_v27_sources.json'
RAW = ROOT / 'data/interim/common_v27'


def build(fetch=False):
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=27, release_date='2026-11-07',
                          age_rule=native_bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
