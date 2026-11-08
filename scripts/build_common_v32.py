"""Append reviewed records from Fucino and Lake Anterne."""
import argparse

import build_common_v19 as pipeline

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v31.json'
CONTRACT = ROOT / 'scripts/importers/common_v32_sources.json'
RAW = ROOT / 'data/interim/common_v32'


def build(fetch=False):
    pipeline.curator.FAMILIES['erosion'] = 'Sedimentología'
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=32, release_date='2026-11-08')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
