from .base import BaseFetcher, FetchingError
from bs4 import BeautifulSoup
from typing import Dict, Any
import logging

logger = logging.getLogger("ExampleVenueFetcher")

class ExampleVenueFetcher(BaseFetcher):
    """
    A template fetcher designed to retrieve detailed information for a single venue.
    """
    def __init__(self, client: httpx.AsyncClient, max_retries: int = 3, timeout: float = 12.0):
        super().__init__(client, max_retries, timeout)
        self.base_url = "https://www.example.com"

    def _parse_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parses the example venue page to extract specific details.
        Assumes a structure where details are in a <div class='venue-details'>.
        """
        venue_details: Dict[str, Any] = {}
        
        details_container = soup.find('div', class_='venue-details')
        
        if not details_container:
            logger.warning("Could not find the main venue details container.")
            return {"status": "partial", "venue_name": "Unknown", "details": {}}

        # Extract Name (assuming it's an H1)
        name_tag = details_container.find('h1', class_='venue-name')
        venue_details['name'] = name_tag.get_text(strip=True) if name_tag else "N/A Name"

        # Extract specific fields
        venue_details['capacity'] = details_container.find('span', class_='detail-capacity').get_text(strip=True) if details_container.find('span', class_='detail-capacity') else "N/A Capacity"
        venue_details['address'] = details_container.find('p', class_='detail-address').get_text(strip=True) if details_container.find('p', class_='detail-address') else "N/A Address"
        venue_details['website'] = details_container.find('a', class_='detail-website')['href'] if details_container.find('a', class_='detail-website') else "N/A Website"

        return {
            "status": "success",
            "source": "ExampleVenue",
            "venue_name": venue_details['name'],
            "details": venue_details
        }

# Example usage (optional, but good for testing)
async def main():
    async with httpx.AsyncClient() as client:
        fetcher = ExampleVenueFetcher(client)
        try:
            # Use the base URL for the fetch
            data = await fetcher.fetch_data(fetcher.base_url)
            print("\n--- Successfully Fetched Example Venue Data ---")
            print(f"Status: {data.get('status')}, Venue: {data.get('venue_name')}")
            print("Details:", data.get('details'))
        except FetchingError as e:
            print(f"\n--- Example Venue Fetching Failed ---")
            print(e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())