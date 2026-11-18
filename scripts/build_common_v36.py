"""Append selected published pollen-based climate reconstructions."""
import argparse

import build_common_v19 as pipeline

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v35.json'
CONTRACT = ROOT / 'scripts/importers/common_v36_sources.json'
RAW = ROOT / 'data/interim/common_v36'


def calendar_bp(header):
    """Retain the source's published calendar age in thousands of years BP."""
    if header.count('Cal age [ka BP]') == 1:
        return header.index('Cal age [ka BP]'), 'identity: source calendar point age in ka BP', float
    return None


def build(fetch=False):
    pipeline.curator.FAMILIES['pollen_climate'] = 'Polen'
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=36, release_date='2026-11-18',
                          age_rule=calendar_bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
