import requests
from bs4 import BeautifulSoup
import csv
import logging
from typing import Dict, Any, List

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Configuration
PLAYER_URL = "https://www.hltv.org/stats/players/15165/blamef?startDate=all"
CSV_OUTPUT_FILE_PATH = 'player_data.csv'

def fetch_page(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.hltv.org/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    response = requests.get(url, headers=headers)
    response.raise_for_status()
    logger.debug(f"Page fetched successfully. Status code: {response.status_code}")
    return response.text

def extract_player_data(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'html.parser')
    player_data = {
        'Basic Info': extract_basic_info(soup),
        'Summary Stats': extract_summary_stats(soup),
        'Detailed Stats': extract_detailed_stats(soup),
        'Role Stats': extract_role_stats(soup)  # New addition
    }
    logger.debug(f"Extracted player data: {player_data}")
    return player_data

def extract_basic_info(soup: BeautifulSoup) -> Dict[str, str]:
    basic_info = {}
    
    player_name = soup.find('h1', class_='summaryNickname')
    if player_name:
        basic_info['Player Name'] = player_name.text.strip()

    real_name = soup.find('div', class_='summaryRealname')
    if real_name:
        basic_info['Real Name'] = real_name.text.strip()

    team_name = soup.find('div', class_='SummaryTeamname')
    if team_name:
        basic_info['Team Name'] = team_name.text.strip()

    player_age = soup.find('div', class_='summaryPlayerAge')
    if player_age:
        basic_info['Age'] = player_age.text.strip()

    logger.debug(f"Extracted basic info: {basic_info}")
    return basic_info

def extract_summary_stats(soup: BeautifulSoup) -> Dict[str, str]:
    summary_stats = {}
    stat_containers = soup.find_all('div', class_='summaryStatBreakdown')
    for container in stat_containers:
        stat_name = container.find('div', class_='summaryStatBreakdownSubHeader')
        stat_value = container.find('div', class_='summaryStatBreakdownDataValue')
        if stat_name and stat_value:
            clean_name = stat_name.text.strip().split('\n')[0]  # Take only the first part of the stat name
            summary_stats[clean_name] = stat_value.text.strip()
    logger.debug(f"Extracted summary stats: {summary_stats}")
    return summary_stats

def extract_detailed_stats(soup: BeautifulSoup) -> Dict[str, str]:
    detailed_stats = {}
    stats_container = soup.find('div', class_='statistics')
    if stats_container:
        stats_rows = stats_container.find_all('div', class_='stats-row')
        for row in stats_rows:
            spans = row.find_all('span')
            if len(spans) == 2:
                stat_name = spans[0].text.strip()
                stat_value = spans[1].text.strip()
                detailed_stats[stat_name] = stat_value
    logger.debug(f"Extracted detailed stats: {detailed_stats}")
    return detailed_stats

# New function to extract role stats
def extract_role_stats(soup: BeautifulSoup) -> Dict[str, Any]:
    role_stats = {}
    role_categories = ['firepower', 'entrying', 'trading', 'opening', 'clutching', 'sniping', 'utility']
    
    for category in role_categories:
        category_div = soup.find('div', class_=f'role-stats-section role-{category}')
        if category_div:
            category_score = category_div.find('div', class_='row-stats-section-score')
            score = category_score.text.strip() if category_score else 'N/A'
            score = f"{score}" if score != 'N/A' else score
            
            substats = {}
            stat_rows = category_div.find_all('div', class_='role-stats-row')
            for row in stat_rows:
                stat_title = row.find('div', class_='role-stats-title')
                stat_data = row.find('div', class_='role-stats-data')
                if stat_title and stat_data:
                    substats[stat_title.text.strip()] = stat_data.text.strip()
            
            role_stats[category.capitalize()] = {
                'Score': score,
                'Substats': substats
            }
    
    logger.debug(f"Extracted role stats: {role_stats}")
    return role_stats

def flatten_player_data(player_data: Dict[str, Any]) -> Dict[str, str]:
    flat_data = {}
    for category, data in player_data.items():
        if isinstance(data, dict):
            if category == 'Role Stats':
                for role, role_data in data.items():
                    flat_data[f"{category}_{role}_Score"] = role_data['Score']
                    for substat, value in role_data['Substats'].items():
                        flat_data[f"{category}_{role}_{substat}"] = str(value)
            else:
                for key, value in data.items():
                    flat_data[f"{category}_{key}"] = str(value)
        else:
            flat_data[category] = str(data)
    logger.debug(f"Flattened player data: {flat_data}")
    return flat_data

def main():
    try:
        html = fetch_page(PLAYER_URL)
        player_data = extract_player_data(html)
        flat_data = flatten_player_data(player_data)

        if not flat_data:
            logger.error("No data was extracted. The CSV file will be empty.")
            return

        with open(CSV_OUTPUT_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=flat_data.keys())
            writer.writeheader()
            writer.writerow(flat_data)
        
        logger.info(f"Player data successfully scraped and saved to {CSV_OUTPUT_FILE_PATH}")
    except Exception as e:
        logger.error(f"An error occurred: {e}", exc_info=True)

if __name__ == "__main__":
    main()