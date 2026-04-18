import abc
import httpx
from bs4 import BeautifulSoup
import asyncio
import logging
from typing import List, Dict, Any

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("BaseFetcher")

class FetchingError(Exception):
    """Custom exception for fetching failures."""
    pass

class BaseFetcher(abc.ABC):
    """
    Abstract Base Class for all Event Aggregator fetchers.
    Defines the interface and common retry logic.
    """
    def __init__(self, client: httpx.AsyncClient, max_retries: int = 3, timeout: float = 10.0):
        self.client = client
        self.max_retries = max_retries
        self.timeout = timeout

    @abc.abstractmethod
    async def fetch_data(self, url: str) -> Dict[str, Any]:
        """
        Fetches and parses data from a given URL.

        :param url: The URL to fetch.
        :return: A dictionary containing the parsed data.
        :raises FetchingError: If fetching or parsing fails after all retries.
        """
        pass

    async def _fetch_with_retry(self, url: str) -> BeautifulSoup:
        """
        Handles the HTTP request with exponential backoff retry logic.
        """
        for attempt in range(self.max_retries):
            try:
                logger.info(f"Attempting to fetch {url} (Attempt {attempt + 1}/{self.max_retries})...")
                response = await self.client.get(url, timeout=self.timeout)
                response.raise_for_status()  # Raises HTTPStatusError for 4xx/5xx responses
                return BeautifulSoup(response.content, 'html.parser')
            
            except httpx.HTTPStatusError as e:
                logger.warning(f"HTTP error fetching {url}: {e.response.status_code} - {e.response.reason_phrase}")
            except httpx.RequestError as e:
                logger.error(f"Request error fetching {url}: {type(e).__name__} - {e}")
            
            if attempt < self.max_retries - 1:
                # Exponential backoff: 2s, 4s, 8s...
                wait_time = 2 ** attempt
                logger.info(f"Waiting {wait_time} seconds before retrying...")
                await asyncio.sleep(wait_time)
            else:
                logger.error(f"Failed to fetch {url} after {self.max_retries} attempts.")
                raise FetchingError(f"Failed to fetch {url} after {self.max_retries} attempts.")

    async def fetch_data(self, url: str) -> Dict[str, Any]:
        """
        (Implementation detail: uses the retry mechanism)
        """
        soup = await self._fetch_with_retry(url)
        return self._parse_data(soup)

    @abc.abstractmethod
    def _parse_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parses the BeautifulSoup object into a structured dictionary.
        This method must be implemented by subclasses.
        """
        pass

# Example usage (optional, but good for testing)
async def main():
    async with httpx.AsyncClient() as client:
        fetcher = BaseFetcher(client)
        try:
            # Using a placeholder URL for testing
            test_url = "https://httpbin.org/html"
            data = await fetcher.fetch_data(test_url)
            print("\n--- Successfully Fetched Data ---")
            print(data)
        except FetchingError as e:
            print(f"\n--- Fetching Failed ---")
            print(e)

if __name__ == "__main__":
    asyncio.run(main())