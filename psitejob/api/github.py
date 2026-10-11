from typing import ClassVar

import requests


class ApiError(Exception):
    pass


class GithubApiClient:
    _default_request_timeout_secs: ClassVar[int] = 10

    def __init__(self, base_url: str):
        self._base_url = base_url

    def get_latest_commits(self, project_name: str) -> list:
        url = f"{self._base_url}/{project_name}/commits"
        try:
            response = requests.get(url, timeout=self._default_request_timeout_secs)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise ApiError(f"Error while requesting {url}") from e
