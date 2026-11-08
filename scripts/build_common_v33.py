"""Append published ecological proxies from Padul and Lake İznik."""
import argparse

import build_common_v19 as pipeline
from build_common_v22 import native_bp

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v32.json'
CONTRACT = ROOT / 'scripts/importers/common_v33_sources.json'
RAW = ROOT / 'data/interim/common_v33'


def build(fetch=False):
    pipeline.curator.FAMILIES['aquatic_palynomorphs'] = 'Micropaleontología'
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=33, release_date='2026-11-08',
                          age_rule=native_bp)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
