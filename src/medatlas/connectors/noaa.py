"""NOAA/NCEI World Data Service for Paleoclimatology JSON search client."""

from urllib.parse import urlencode, urljoin

from .base import HTTPConnector, ConnectorError


class NOAAWDSConnector(HTTPConnector):
    source = "noaa_wds_paleo"
    search_url = "https://www.ncei.noaa.gov/access/paleo-search/study/search.json"
    params_url = "https://www.ncei.noaa.gov/access/paleo-search/study/params.json"

    def search_studies(self, **parameters):
        """Return one page exactly as supplied by NOAA plus provenance artifact.

        NOAA limits full-study searches to ten records/page; use ``next_page``
        until it returns None. For broad surveys, set headersOnly=true.
        """
        allowed = {key: value for key, value in parameters.items() if value is not None}
        url = f"{self.search_url}?{urlencode(allowed)}"
        payload, artifact = self.get_json(url)
        if not isinstance(payload, dict) or "study" not in payload:
            raise ConnectorError("NOAA response lacks the expected 'study' field")
        return payload, artifact

    def next_page(self, payload: dict) -> str | None:
        pages = payload.get("page") or []
        next_url = pages[0].get("next") if pages else None
        return urljoin(self.search_url, next_url) if next_url else None

    def fetch_page(self, page_url: str):
        """Fetch the exact continuation URL returned by NOAA."""
        return self.get_json(page_url)

    def search_params(self, *, data_type_id: int | None = None):
        url = self.params_url
        if data_type_id is not None:
            url += "?" + urlencode({"dataTypeId": data_type_id})
        return self.get_json(url)

    def data_search_preview(self, **parameters):
        """Ask NOAA for a file preview; callers must inspect publisher/rights."""
        allowed = {"preview": "true", **{k: v for k, v in parameters.items() if v is not None}}
        return self.get_json("https://www.ncei.noaa.gov/access/paleo-search/data/search.json?" + urlencode(allowed))
