"""Append Balearic and Balkan proxy observations using their archived ages."""
import argparse

import build_common_v19 as pipeline
from build_common_v22 import native_bp

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v24.json'
CONTRACT = ROOT / 'scripts/importers/common_v25_sources.json'
RAW = ROOT / 'data/interim/common_v25'


def reviewed_age(header):
    ohrid = 'Age [ka BP] (Nature Oktober 2018)'
    if ohrid in header:
        return header.index(ohrid), 'identity: source Ohrid composite point age in ka BP', float
    return native_bp(header)


def build(fetch=False):
    pipeline.curator.FAMILIES.update(magnetism='Sedimentología', microfossils='Micropaleontología')
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=25, release_date='2026-11-07',
                          age_rule=reviewed_age)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
