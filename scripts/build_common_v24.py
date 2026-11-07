"""Append the dated Frigola proxy tables from two Gulf of Lions archives."""
import argparse

import build_common_v19 as pipeline

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v23.json'
CONTRACT = ROOT / 'scripts/importers/common_v24_sources.json'
RAW = ROOT / 'data/interim/common_v24'


def calendar_bp(header):
    """Read the published calendar ages directly, in ka BP."""
    if header.count('Cal age [ka BP]') == 1:
        return header.index('Cal age [ka BP]'), 'identity: source calendar point age in ka BP', float
    return None


def build(fetch=False):
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=24, release_date='2026-11-07',
                          age_rule=calendar_bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
