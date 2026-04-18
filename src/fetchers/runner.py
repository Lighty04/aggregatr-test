import asyncio
import httpx
import logging
from typing import List, Dict, Any

# Import the fetcher modules
from .base import BaseFetcher, FetchingError
from .philharmonie import PhilharmonieFetcher
from .example_venue import ExampleVenueFetcher

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("FetcherRunner")

class FetcherRunner:
    """
    Manages and executes multiple fetchers concurrently.
    """
    def __init__(self, fetchers: List[BaseFetcher]):
        self.fetchers = fetchers
        self.client = httpx.AsyncClient()

    async def run_all(self) -> List[Dict[str, Any]]:
        """
        Runs all registered fetchers concurrently and collects their results.
        """
        logger.info(f"Starting concurrent fetch for {len(self.fetchers)} fetchers...")
        
        # Create a list of coroutines (tasks)
        tasks = [fetcher.fetch_data(f"URL_TO_BE_OVERRIDDEN_BY_FETCHER") for fetcher in self.fetchers]
        
        # Run tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        final_results: List[Dict[str, Any]] = []
        
        # Process results
        for i, result in enumerate(results):
            fetcher_name = self.fetchers[i].__class__.__name__
            
            if isinstance(result, FetchingError):
                logger.error(f"[{fetcher_name}] Failed with FetchingError: {result}")
                final_results.append({
                    "fetcher": fetcher_name,
                    "status": "error",
                    "message": str(result)
                })
            elif isinstance(result, Exception):
                logger.error(f"[{fetcher_name}] Failed with unexpected exception: {type(result).__name__} - {result}")
                final_results.append({
                    "fetcher": fetcher_name,
                    "status": "error",
                    "message": f"Unexpected exception: {type(result).__name__}"
                })
            else:
                logger.info(f"[{fetcher_name}] Successfully fetched data. Status: {result.get('status')}")
                final_results.append(result)
                
        return final_results

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()

async def main():
    # 1. Initialize fetchers
    # Note: The URL passed to the runner is a placeholder; each fetcher overrides it internally.
    philharmonie_fetcher = PhilharmonieFetcher(httpx.AsyncClient())
    example_venue_fetcher = ExampleVenueFetcher(httpx.AsyncClient())
    
    # We can add more fetchers here easily
    # custom_fetcher = CustomFetcher(httpx.AsyncClient()) 
    
    fetchers_to_run = [
        philharmonie_fetcher,
        example_venue_fetcher,
        # custom_fetcher
    ]

    # 2. Run the runner
    async with FetcherRunner(fetchers_to_run) as runner:
        all_results = await runner.run_all()
        
        print("\n==================================================")
        print("✅ ALL FETCHING COMPLETE")
        print("==================================================")
        
        # 3. Display summary
        for result in all_results:
            fetcher = result.get('fetcher', 'Unknown')
            status = result.get('status', 'N/A')
            print(f"\n--- {fetcher} ({status.upper()}) ---")
            
            if status == 'success':
                print(f"Source: {result.get('source')}")
                if fetcher == 'PhilharmonieFetcher':
                    print(f"Total Events: {result.get('count')}")
                    print("First Event Details:", result['events'][0])
                elif fetcher == 'ExampleVenueFetcher':
                    print(f"Venue Name: {result.get('venue_name')}")
                    print("Capacity:", result['details'].get('capacity'))
                    print("Address:", result['details'].get('address'))
            elif status == 'error':
                print(f"Error Message: {result.get('message')}")

if __name__ == "__main__":
    asyncio.run(main())