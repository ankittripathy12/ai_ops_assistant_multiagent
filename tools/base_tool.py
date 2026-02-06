from abc import ABC, abstractmethod
from typing import Any, Dict
import requests
from config import Config


class BaseTool(ABC):
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description

    @abstractmethod
    def execute(self, **kwargs) -> Dict[str, Any]:
        """Execute the tool with given parameters"""
        pass

    def make_request(self,
                     method: str,
                     url: str,
                     headers: Dict = None,
                     params: Dict = None,
                     data: Dict = None,
                     max_retries: int = None) -> Dict[str, Any]:
        """Make HTTP request with retry logic"""
        max_retries = max_retries or Config.MAX_RETRIES

        for attempt in range(max_retries):
            try:
                response = requests.request(
                    method=method,
                    url=url,
                    headers=headers,
                    params=params,
                    json=data,
                    timeout=Config.REQUEST_TIMEOUT
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                if attempt == max_retries - 1:
                    raise Exception(f"Request failed after {max_retries} attempts: {str(e)}")
                continue

        raise Exception("Request failed")