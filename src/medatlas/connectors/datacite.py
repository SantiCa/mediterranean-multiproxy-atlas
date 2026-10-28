"""Cross-repository DOI discovery through DataCite's public REST API."""

from urllib.parse import urlencode, quote
import re

from .base import HTTPConnector


class DataCiteConnector(HTTPConnector):
    source = "datacite"
    api_url = "https://api.datacite.org/dois"

    def search(self, query: str, *, page_size: int = 25, page_number: int = 1):
        if not 1 <= page_size <= 1000:
            raise ValueError("DataCite page_size must be between 1 and 1000")
        if page_number < 1:
            raise ValueError("page_number must be positive")
        params = urlencode({"query": query, "page[size]": page_size, "page[number]": page_number})
        return self.get_json(f"{self.api_url}?{params}")

    def fetch_doi(self, doi: str):
        normalized = doi.strip().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
        if not re.fullmatch(r"10\.\d{4,9}/\S+", normalized):
            raise ValueError("Expected a DOI")
        return self.get_json(f"{self.api_url}/{quote(normalized, safe='/')}")
