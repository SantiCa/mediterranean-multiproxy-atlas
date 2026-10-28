"""Neotoma Paleoecology Database v2.0 read-only search/download client."""

from urllib.parse import urlencode

from .base import HTTPConnector, ConnectorError


class NeotomaConnector(HTTPConnector):
    source = "neotoma"
    api_root = "https://api.neotomadb.org/v2.0"

    def _get_endpoint(self, path: str, **parameters):
        query = urlencode({k: v for k, v in parameters.items() if v is not None}, doseq=True)
        url = f"{self.api_root}/{path.lstrip('/')}" + (f"?{query}" if query else "")
        return self.get_json(url)

    def search_sites(self, **parameters):
        return self._get_endpoint("data/sites", **parameters)

    def search_datasets(self, **parameters):
        return self._get_endpoint("data/datasets", **parameters)

    def site_datasets(self, site_id: int):
        return self._get_endpoint(f"data/sites/{int(site_id)}/datasets")

    def dataset_metadata(self, dataset_id: int):
        return self._get_endpoint(f"data/datasets/{int(dataset_id)}")

    def dataset_chronologies(self, dataset_id: int):
        return self._get_endpoint(f"data/datasets/{int(dataset_id)}/chronologies")

    def download_dataset(self, dataset_id: int):
        payload, artifact = self._get_endpoint(f"data/downloads/{int(dataset_id)}")
        if not isinstance(payload, dict):
            raise ConnectorError("Neotoma download response is not a JSON object")
        return payload, artifact
