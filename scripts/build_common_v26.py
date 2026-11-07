"""Append reviewed western Mediterranean and Nile margin proxy series."""
import argparse

import build_common_v19 as pipeline
from build_common_v22 import native_bp

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v25.json'
CONTRACT = ROOT / 'scripts/importers/common_v26_sources.json'
RAW = ROOT / 'data/interim/common_v26'


def build(fetch=False):
    pipeline.curator.FAMILIES.update(organic_isotopes='Isótopos estables',
                                    mineralogy='Mineralogía')
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=26, release_date='2026-11-07',
                          age_rule=native_bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
