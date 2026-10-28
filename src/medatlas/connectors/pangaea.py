"""PANGAEA DOI retrieval and OAI-PMH metadata harvest."""

from urllib.parse import urlencode
import re

from .base import HTTPConnector, ConnectorError


class PANGAEAConnector(HTTPConnector):
    """Retrieve original bytes; XML metadata/OAI error elements need caller review.

    Dataset tables are signature-checked; collections must be resolved into their
    citable children before requesting measurements.
    """
    source = "pangaea"
    base_url = "https://doi.pangaea.de"
    oai_url = "https://ws.pangaea.de/oai/provider"

    @staticmethod
    def normalize_doi(doi: str) -> str:
        value = doi.strip().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
        if not re.fullmatch(r"10\.1594/pangaea\.[0-9]+", value, re.IGNORECASE):
            raise ValueError(f"Expected a PANGAEA DOI, got {doi!r}")
        return "10.1594/PANGAEA." + value.rsplit(".", 1)[1]

    def dataset_table(self, doi: str):
        doi = self.normalize_doi(doi)
        url = f"{self.base_url}/{doi}?format=textfile"
        # An explicit format parameter suffices. Live checks returned HTTP 400
        # with Accept headers and byte-identical valid TSV without that header.
        artifact = self.get(url, accept=None)
        # Collections and access pages are not tabular measurements, even on HTTP 200.
        if b"/* DATA DESCRIPTION:" not in artifact.body or b"*/" not in artifact.body:
            raise ConnectorError(f"PANGAEA response is not a text table: {url}")
        return artifact

    def dataset_metadata(self, doi: str):
        doi = self.normalize_doi(doi)
        url = f"{self.base_url}/{doi}?format=metadata_datacite4"
        return self.get(url, accept="application/xml, text/xml;q=0.9")

    def oai_record(self, doi: str, metadata_prefix: str = "oai_dc"):
        doi = self.normalize_doi(doi)
        identifier = f"oai:pangaea.de:doi:{doi}"
        query = urlencode({"verb": "GetRecord", "metadataPrefix": metadata_prefix, "identifier": identifier})
        return self.get(f"{self.oai_url}?{query}", accept="application/xml, text/xml;q=0.9")

    def oai_list_records(self, *, metadata_prefix: str = "oai_dc", set_name: str | None = "citable",
                         from_date: str | None = None, until_date: str | None = None,
                         resumption_token: str | None = None):
        params = {"verb": "ListRecords"}
        if resumption_token:
            params["resumptionToken"] = resumption_token
        else:
            params["metadataPrefix"] = metadata_prefix
            if set_name:
                params["set"] = set_name
            if from_date:
                params["from"] = from_date
            if until_date:
                params["until"] = until_date
        return self.get(f"{self.oai_url}?{urlencode(params)}", accept="application/xml, text/xml;q=0.9")
