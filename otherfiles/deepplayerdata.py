import requests
from bs4 import BeautifulSoup
import csv
from typing import Dict, Any, List
import time
import random

# Configuration
INPUT_CSV_FILE_PATH = '../data/player_urls.csv'
OUTPUT_CSV_FILE_PATH = '../data/deep_player_data.csv'

def read_urls_from_csv(file_path: str) -> List[str]:
    with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header row
        return [row[0] for row in reader if row]

def fetch_page(url: str) -> str:
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'Referer': 'https://www.hltv.org/',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Cache-Control': 'max-age=0',
    }
    url_with_param = f"{url}?startDate=all"
    
    # Randomize the delay between requests (2 to 5 seconds)
    time.sleep(random.uniform(2, 5))
    
    session = requests.Session()
    
    # First, visit the main page to set cookies
    session.get("https://www.hltv.org/", headers=headers)
    
    # Then visit the actual player page
    response = session.get(url_with_param, headers=headers)
    response.raise_for_status()
    return response.text

def extract_player_data(html: str) -> Dict[str, Any]:
    soup = BeautifulSoup(html, 'html.parser')
    return {
        'Basic Info': extract_basic_info(soup),
        'Summary Stats': extract_summary_stats(soup),
        'Detailed Stats': extract_detailed_stats(soup),
        'Role Stats': extract_role_stats(soup)
    }

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
    return basic_info

def extract_summary_stats(soup: BeautifulSoup) -> Dict[str, str]:
    summary_stats = {}
    stat_containers = soup.find_all('div', class_='summaryStatBreakdown')
    for container in stat_containers:
        stat_name = container.find('div', class_='summaryStatBreakdownSubHeader')
        stat_value = container.find('div', class_='summaryStatBreakdownDataValue')
        if stat_name and stat_value:
            clean_name = stat_name.text.strip().split('\n')[0]
            summary_stats[clean_name] = stat_value.text.strip()
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
    return detailed_stats

def extract_role_stats(soup: BeautifulSoup) -> Dict[str, Any]:
    role_stats = {}
    role_categories = ['firepower', 'entrying', 'trading', 'opening', 'clutching', 'sniping', 'utility']
    
    for category in role_categories:
        category_div = soup.find('div', class_=f'role-stats-section role-{category}')
        if category_div:
            category_score = category_div.find('div', class_='row-stats-section-score')
            score = category_score.text.strip() if category_score else 'N/A'
            
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
    return flat_data

def process_url(url: str) -> Dict[str, str]:
    try:
        html = fetch_page(url)
        player_data = extract_player_data(html)
        flat_data = flatten_player_data(player_data)
        flat_data['URL'] = url
        player_name = flat_data.get('Basic Info_Player Name', 'Unknown Player')
        print(f"Data gathered for {player_name} - {len(flat_data)} data points")
        return flat_data
    except Exception as e:
        print(f"An error occurred while processing {url}: {e}")
        return {}

def main():
    try:
        player_urls = read_urls_from_csv(INPUT_CSV_FILE_PATH)
        print(f"Loaded {len(player_urls)} URLs from {INPUT_CSV_FILE_PATH}")

        all_player_data = []
        processed_count = 0

        try:
            for url in player_urls:
                player_data = process_url(url)
                if player_data:
                    all_player_data.append(player_data)
                processed_count += 1

        except KeyboardInterrupt:
            print("\nScript interrupted by user. Saving progress...")
        
        finally:
            if all_player_data:
                fieldnames = set()
                for player_data in all_player_data:
                    fieldnames.update(player_data.keys())

                with open(OUTPUT_CSV_FILE_PATH, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    for player_data in all_player_data:
                        writer.writerow(player_data)
                
                print(f"Player data successfully scraped and saved to {OUTPUT_CSV_FILE_PATH}")
            
            print(f"Total players processed: {processed_count} out of {len(player_urls)}")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()