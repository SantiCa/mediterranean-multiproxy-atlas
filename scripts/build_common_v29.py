"""Append published planktonic foraminiferal assemblages from the Adriatic."""
import argparse

import build_common_v19 as pipeline
from build_common_v22 import native_bp

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v28.json'
CONTRACT = ROOT / 'scripts/importers/common_v29_sources.json'
RAW = ROOT / 'data/interim/common_v29'


def build(fetch=False):
    pipeline.curator.FAMILIES['planktonic_counts'] = 'Foraminíferos'
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=29, release_date='2026-11-07',
                          age_rule=native_bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
