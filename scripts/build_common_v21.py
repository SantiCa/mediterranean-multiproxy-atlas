"""Append verified native susceptibility, SST, isotope and XRF records."""
import argparse

import build_common_v19 as pipeline

ROOT = pipeline.ROOT
BASE = ROOT / 'data/processed/atlas-v20.json'
CONTRACT = ROOT / 'scripts/importers/common_v21_sources.json'
RAW = ROOT / 'data/interim/common_v21'


def build(fetch=False):
    pipeline.curator.FAMILIES.update(magnetism='Sedimentología',
                                    ostracod_isotopes='Isótopos estables')
    return pipeline.build(fetch, baseline=BASE, contract_path=CONTRACT,
                          raw_dir=RAW, version=21, release_date='2026-11-07')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--fetch', action='store_true')
    build(parser.parse_args().fetch)
