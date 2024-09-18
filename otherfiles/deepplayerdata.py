import aiohttp
import asyncio
from bs4 import BeautifulSoup
import csv
import json
import logging
import random
from typing import List, Dict, Any, Optional
from aiohttp import ClientSession
from tenacity import retry, stop_after_attempt, wait_random

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
CSV_FILE_PATH = 'urls.csv'
OUTPUT_FILE_PATH = 'player_data.json'
MAX_CONCURRENT_REQUESTS = 10
MIN_DELAY = 1
MAX_DELAY = 3

async def read_urls_from_csv(file_path: str) -> List[str]:
    urls = []
    try:
        with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
            csvreader = csv.reader(csvfile)
            for row in csvreader:
                if row:  # Ensure the row is not empty
                    urls.append(row[0].strip())  # Assuming the URL is in the first column
    except FileNotFoundError:
        logger.error(f"CSV file not found: {file_path}")
    except PermissionError:
        logger.error(f"Permission denied when trying to read: {file_path}")
    except Exception as e:
        logger.error(f"An error occurred while reading CSV: {e}")
    return urls

@retry(stop=stop_after_attempt(3), wait=wait_random(min=MIN_DELAY, max=MAX_DELAY))
async def fetch_page(session: ClientSession, url: str) -> Optional[str]:
    full_url = f"{url}?startDate=all"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36'
    }
    try:
        async with session.get(full_url, headers=headers) as response:
            if response.status == 200:
                return await response.text()
            else:
                logger.warning(f"Request to {full_url} returned status code {response.status}")
                return None
    except aiohttp.ClientError as e:
        logger.error(f"An error occurred while requesting {full_url}: {e}")
        return None

def extract_player_data(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'html.parser')
    player_stats = {
        'Player Name': "Unknown",
        'Team Name': None,
        'Teammates': [],
        'Role Stats': {},
        'General Stats': {}
    }

    # Extract player name
    player_name = soup.find('h1', class_='summaryNickname')
    if player_name:
        player_stats['Player Name'] = player_name.text.strip()

    # Extract team name
    team_name = soup.find('a', class_='SummaryTeamname')
    if team_name:
        player_stats['Team Name'] = team_name.text.strip()

    # Extract teammates
    teammates_section = soup.find('div', class_='grid teammates')
    if teammates_section:
        teammates = teammates_section.find_all('div', class_='teammate-info')
        player_stats['Teammates'] = [teammate.find('span').text.strip() for teammate in teammates if teammate.find('span')]

    # Extract role stats
    role_stats_sections = soup.find_all('div', class_='role-stats-section')
    for section in role_stats_sections:
        section_name = next((cls.replace('role-', '') for cls in section.get('class', []) if cls.startswith('role-')), None)
        if not section_name:
            continue
        player_stats['Role Stats'][section_name] = {}
        stat_titles = section.find_all('div', class_='role-stats-title')
        stat_values = section.find_all('div', class_='role-stats-data')
        for title, value in zip(stat_titles, stat_values):
            player_stats['Role Stats'][section_name][title.text.strip()] = value.text.strip()

    # Extract general statistics
    statistics_section = soup.find('div', class_='statistics')
    if statistics_section:
        stats_rows = statistics_section.find_all('div', class_='stats-row')
        for row in stats_rows:
            spans = row.find_all('span')
            if len(spans) >= 2:
                player_stats['General Stats'][spans[0].text.strip()] = spans[1].text.strip()

    return player_stats

async def process_url(session: ClientSession, url: str) -> Optional[Dict[str, Any]]:
    html = await fetch_page(session, url)
    if html:
        return extract_player_data(html)
    return None

async def main():
    urls = await read_urls_from_csv(CSV_FILE_PATH)
    all_player_data = []

    async with aiohttp.ClientSession() as session:
        tasks = [process_url(session, url) for url in urls]
        results = await asyncio.gather(*tasks)

        for result in results:
            if result:
                all_player_data.append(result)
                logger.info(f"Processed player: {result['Player Name']}")

    # Save data to JSON file
    with open(OUTPUT_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(all_player_data, f, ensure_ascii=False, indent=4)

    logger.info(f"Scraping completed. Data saved to {OUTPUT_FILE_PATH}")

if __name__ == "__main__":
    asyncio.run(main())