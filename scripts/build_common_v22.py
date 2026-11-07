"""Append reviewed Lake Lungo, Tagus shelf and Alboran Sea series."""
import argparse

import build_common_v19 as pipeline

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v21.json'
CONTRACT = ROOT / 'scripts/importers/common_v22_sources.json'
RAW = ROOT / 'data/interim/common_v22'


def native_bp(header):
    """Use the archived BP column when the source also supplies CE."""
    if header.count('Age [ka BP]') == 1:
        return header.index('Age [ka BP]'), 'identity: source point age in ka BP', float
    return None


def build(fetch=False):
    pipeline.curator.FAMILIES['magnetism'] = 'Sedimentología'
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=22, release_date='2026-11-07',
                          age_rule=native_bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
