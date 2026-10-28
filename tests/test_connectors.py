"""Offline regressions for provider requests, native payloads and provenance."""
from datetime import datetime, timezone
import hashlib
import io
import json
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import patch
from urllib.parse import parse_qs, urlsplit
from zipfile import ZipFile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from medatlas.connectors import DataCiteConnector, LiPDArchive, NOAAWDSConnector, PANGAEAConnector
from medatlas.connectors.base import ConnectorError, HTTPConnector, preserve_raw
from medatlas.models import RetrievedArtifact
from seed_query import select


def artifact(body=b"{}"):
    return RetrievedArtifact("example", "https://example.org/data", "https://example.org/data",
                             datetime.now(timezone.utc), "application/json",
                             hashlib.sha256(body).hexdigest(), body)


class ConnectorContracts(unittest.TestCase):
    def test_pangaea_explicit_table_format_omits_accept_header(self):
        client=PANGAEAConnector()
        with patch.object(client,'get',return_value=artifact(b'/* DATA DESCRIPTION: x */\nage\tvalue')) as get:
            client.dataset_table('10.1594/PANGAEA.438816')
        self.assertIsNone(get.call_args.kwargs['accept'])

    def test_pangaea_does_not_accept_html_as_measurements(self):
        with patch.object(PANGAEAConnector, "get", return_value=artifact(b"<html>Access required</html>")):
            with self.assertRaises(ConnectorError):
                PANGAEAConnector().dataset_table("10.1594/PANGAEA.438816")

    def test_pangaea_doi_rejects_url_parameter_injection(self):
        client = PANGAEAConnector()
        self.assertEqual(client.normalize_doi("https://doi.org/10.1594/pangaea.438816"), "10.1594/PANGAEA.438816")
        for bad in ("10.1594/PANGAEA.1?format=other", "10.1594/PANGAEA.", "10.1234/other"):
            with self.assertRaises(ValueError):
                client.dataset_table(bad)

    def test_oai_continuation_uses_only_verb_and_token(self):
        client = PANGAEAConnector()
        with patch.object(client, "get") as request:
            client.oai_list_records(resumption_token="a+b=1", from_date="2020-01-01")
        query = parse_qs(urlsplit(request.call_args.args[0]).query)
        self.assertEqual(query, {"verb": ["ListRecords"], "resumptionToken": ["a+b=1"]})

    def test_noaa_boolean_encoding_and_no_download_from_preview(self):
        client = NOAAWDSConnector()
        with patch.object(client, "get_json", return_value=({"study": []}, artifact())) as request:
            client.search_studies(headersOnly=True)
            self.assertEqual(parse_qs(urlsplit(request.call_args.args[0]).query)["headersOnly"], ["true"])
            client.data_search_preview(preview=False)
            self.assertEqual(parse_qs(urlsplit(request.call_args.args[0]).query)["preview"], ["true"])

    def test_noaa_pagination_and_schema_failure(self):
        client = NOAAWDSConnector()
        self.assertIsNone(client.next_page({"page": []}))
        self.assertEqual(client.next_page({"page": [{"next": "?skip=10"}]}), client.search_url + "?skip=10")
        with self.assertRaises(ConnectorError):
            client.next_page({"page": "unexpected"})
        with self.assertRaises(ConnectorError):
            client.fetch_page("https://another-provider.example/data")
        with patch.object(client, "get_json", return_value=({"error": "schema"}, artifact())):
            with self.assertRaises(ConnectorError):
                client.search_studies()

    def test_datacite_doi_query_characters_are_encoded(self):
        client = DataCiteConnector()
        with patch.object(client, "get_json") as request:
            client.fetch_doi("10.1234/item?x=1#part")
        self.assertNotIn("?", request.call_args.args[0])
        self.assertIn("%3F", request.call_args.args[0])
        with self.assertRaises(ValueError):
            client.search("climate", page_number=0)

    def test_json_scalar_is_rejected(self):
        with patch.object(HTTPConnector, "get", return_value=artifact(b"null")):
            with self.assertRaises(ConnectorError):
                HTTPConnector().get_json("https://example.org/data")

    def test_http_size_limit_is_enforced(self):
        response = io.BytesIO(b"12345")
        with patch("medatlas.connectors.base.urlopen", return_value=response):
            with self.assertRaises(ConnectorError):
                HTTPConnector().get("https://example.org/data", max_bytes=4)

    def test_raw_hash_idempotence_and_manifest_contention(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            raw = artifact(b'{"value": 0}')
            target = preserve_raw(raw, root, "json")
            preserve_raw(raw, root, "json")
            self.assertEqual(target.read_bytes(), raw.body)
            manifest = root / "data/provenance/example_retrievals.json"
            self.assertEqual(len(json.loads(manifest.read_text())), 1)
            manifest.with_suffix(".lock").touch()
            with self.assertRaises(ConnectorError):
                preserve_raw(raw, root, "json")

    def test_raw_rejects_forged_hash_and_path_escape(self):
        from dataclasses import replace
        with tempfile.TemporaryDirectory() as directory:
            for bad in (replace(artifact(), sha256="0" * 64), replace(artifact(), source="../escape")):
                with self.assertRaises(ConnectorError):
                    preserve_raw(bad, Path(directory), "json")
            with self.assertRaises(ConnectorError):
                preserve_raw(artifact(), Path(directory), "../outside")

    def test_lipd_preserves_metadata_and_rejects_ambiguous_packages(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "example.lpd"
            with ZipFile(path, "w") as archive:
                archive.writestr("bag/data/metadata.jsonld", '{"dataSetName":"example"}')
                archive.writestr("bag/data/values.csv", "0,1\n")
            result = LiPDArchive(path).inspect()
            self.assertEqual(result["metadata"]["dataSetName"], "example")
            self.assertEqual(result["table_paths"], ["bag/data/values.csv"])
            with ZipFile(path, "a") as archive:
                archive.writestr("other/metadata.jsonld", "{}")
            with self.assertRaises(ConnectorError):
                LiPDArchive(path).inspect()

    def test_missing_publication_year_is_not_zero(self):
        rows = [{"publication_year": None, "age_ka_bp": 1}]
        self.assertEqual(select(rows), rows)
        self.assertEqual(select(rows, paper_year_min=2000), [])


if __name__ == "__main__":
    unittest.main()
