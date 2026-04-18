from .base import BaseFetcher, FetchingError
from bs4 import BeautifulSoup
from typing import Dict, Any, List
import httpx
import logging

logger = logging.getLogger("PhilharmonieFetcher")

class PhilharmonieFetcher(BaseFetcher):
    """
    Fetches and parses event data specifically from the Philharmonie de Paris website.
    """
    def __init__(self, client: httpx.AsyncClient, max_retries: int = 4, timeout: float = 15.0):
        super().__init__(client, max_retries, timeout)
        self.base_url = "https://www.philharmonie.fr"

    def _parse_data(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """
        Parses the Philharmonie homepage to extract a list of upcoming events.
        Assumes events are listed in a specific container (e.g., 'event-list').
        """
        events: List[Dict[str, Any]] = []
        
        # Target the main event listing container
        event_list_container = soup.find('div', class_='event-list')
        
        if not event_list_container:
            logger.warning("Could not find the main event list container on the Philharmonie page.")
            return {"status": "partial", "events": []}

        # Find all individual event cards
        event_cards = event_list_container.find_all('div', class_='event-card')

        for card in event_cards:
            try:
                # Extract Title
                title_tag = card.find('h3', class_='event-title')
                title = title_tag.get_text(strip=True) if title_tag else "N/A Title"

                # Extract Date/Time
                date_tag = card.find('div', class_='event-date')
                date_time = date_tag.get_text(strip=True) if date_tag else "Date/Time N/A"

                # Extract Venue
                venue_tag = card.find('span', class_='event-venue')
                venue = venue_tag.get_text(strip=True) if venue_tag else "Unknown Venue"

                # Extract Link (assuming the card itself is the link or contains one)
                link_tag = card.find('a', class_='event-card-link')
                relative_url = link_tag.get('href') if link_tag else None
                
                full_url = f"{self.base_url}{relative_url}" if relative_url else "N/A URL"

                events.append({
                    "title": title,
                    "date_time": date_time,
                    "venue": venue,
                    "url": full_url
                })
            
            except Exception as e:
                logger.error(f"Error parsing an event card: {e}")
                continue

        return {
            "status": "success",
            "source": "Philharmonie",
            "count": len(events),
            "events": events
        }

# Example usage (optional, but good for testing)
async def main():
    async with httpx.AsyncClient() as client:
        fetcher = PhilharmonieFetcher(client)
        try:
            # Use the base URL for the fetch
            data = await fetcher.fetch_data(fetcher.base_url)
            print("\n--- Successfully Fetched Philharmonie Data ---")
            print(f"Status: {data.get('status')}, Count: {data.get('count')}")
            if data.get('events'):
                print("First Event:", data['events'][0])
        except FetchingError as e:
            print(f"\n--- Philharmonie Fetching Failed ---")
            print(e)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())