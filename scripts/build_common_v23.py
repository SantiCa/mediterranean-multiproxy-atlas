"""Append archived GDGT reconstructions, alkenones and U1387 isotopes."""
import argparse

import build_common_v19 as pipeline
from build_common_v22 import native_bp

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v22.json'
CONTRACT = ROOT / 'scripts/importers/common_v23_sources.json'
RAW = ROOT / 'data/interim/common_v23'


def reviewed_age(header):
    """Use the explicit LR04 column in the U1387 isotope table."""
    lr04 = 'Age [ka BP] (Age model according to Lisiec...)'
    if lr04 in header:
        return header.index(lr04), 'identity: source LR04 point age in ka BP', float
    return native_bp(header)


def build(fetch=False):
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=23, release_date='2026-11-07',
                          age_rule=reviewed_age)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
