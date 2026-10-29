"""Compare every deployed V28 snapshot asset with the checked local build.

Read-only; no D1 bootstrap or observation API. Optional official Sites service
access is read through hidden stdin and accepted only for this exact Site origin.
The snapshot must first pass node scripts/check-snapshot.mjs against its seed.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import getpass
import hashlib
import json
from pathlib import Path
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import Request, HTTPRedirectHandler, build_opener

SITE = 'https://mediterranean-multiproxy-atlas.nimblequail260.chatgpt.site'


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--url', required=True)
    parser.add_argument('--snapshot', required=True, type=Path)
    parser.add_argument('--report', required=True, type=Path)
    parser.add_argument('--site-service-access', action='store_true')
    args = parser.parse_args()
    origin = args.url.rstrip('/')
    parsed = urlsplit(origin)
    if origin != SITE and not (parsed.scheme == 'http' and parsed.hostname in ('localhost', '127.0.0.1') and parsed.path == ''):
        raise ValueError('Use the exact Sites origin or a local HTTP preview')
    headers = {'User-Agent': 'MedAtlas/static-snapshot-validation'}
    if args.site_service_access:
        if origin != SITE:
            raise ValueError('Service credential is restricted to this exact Sites origin')
        headers['OAI-Sites-Authorization'] = 'Bearer ' + getpass.getpass('Sites service credential (hidden): ')

    class SameOrigin(HTTPRedirectHandler):
        def redirect_request(self, request, fp, code, msg, response_headers, newurl):
            if urlsplit(newurl).netloc != parsed.netloc or urlsplit(newurl).scheme != parsed.scheme:
                raise ValueError('Refusing cross-origin redirect, preserving credential scope')
            return super().redirect_request(request, fp, code, msg, response_headers, newurl)

    def get(path):
        """Bound each response below the static-asset size limit; never mutate."""
        request = Request(origin + path, headers=headers)
        try:
            with build_opener(SameOrigin()).open(request, timeout=45) as response:
                body = response.read(25 * 2**20 + 1)
                if len(body) > 25 * 2**20:
                    raise ValueError('Oversized static asset')
                return response.status, body
        except HTTPError as exc:
            return exc.code, b''

    snapshot = args.snapshot.resolve()
    files = sorted(path for path in snapshot.rglob('*') if path.is_file())
    if not files or not (snapshot / 'catalog.json').is_file():
        raise ValueError('Missing checked snapshot directory')

    def compare(path):
        relative = path.relative_to(snapshot).as_posix()
        status, body = get('/snapshot/' + relative)
        want = hashlib.sha256(path.read_bytes()).hexdigest()
        actual = hashlib.sha256(body).hexdigest()
        if status != 200 or actual != want:
            raise ValueError(f'Static asset differs: {relative}, HTTP {status}')
        return dict(path=relative, sha256=actual, bytes=len(body))

    with ThreadPoolExecutor(max_workers=6) as pool:
        assets = list(pool.map(compare, files))
    status, body = get('/api/private/session')
    if status != 200:
        raise ValueError(f'Private-area status unavailable: HTTP {status}')
    private = json.loads(body)
    removed = {}
    for endpoint in ('catalog', 'observations', 'bootstrap', 'inventory'):
        status, _ = get('/api/' + endpoint)
        removed[endpoint] = status
        if status != 404:
            raise ValueError(f'Removed route still responds: {endpoint}, HTTP {status}')
    catalog = json.loads((snapshot / 'catalog.json').read_bytes())
    report = dict(url=origin, checked_at_utc=datetime.now(timezone.utc).isoformat(),
        release=catalog['release'], records=len(catalog['records']), series=len(catalog['series']),
        groups=len(catalog['snapshot']['groups']), checked_static_files=len(assets),
        all_static_assets_identical=True, private_session_status=private,
        removed_public_api_http_status=removed, assets=assets,
        limitation='Byte equality to the locally cell-checked snapshot; not independent scientific validation or a production D1 schema query')
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    print(json.dumps({key: value for key, value in report.items() if key != 'assets'}, ensure_ascii=False))


if __name__ == '__main__':
    main()
