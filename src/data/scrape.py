import requests
from bs4 import BeautifulSoup
import time
import random
import csv
from urllib.parse import urljoin
import logging
from fake_useragent import UserAgent

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize UserAgent
ua = UserAgent()

def fetch_page(url, retries=3, backoff_factor=0.3):
    headers = {'User-Agent': ua.random}
    
    for i in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            if i == retries - 1:
                logging.error(f"Error fetching {url}: {e}")
                return None
            else:
                time.sleep((backoff_factor * (2 ** i)) + random.uniform(0, 0.1))

def parse_player_stats(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    players = []
    
    table = soup.find('table', class_='stats-table player-ratings-table')
    if table:
        rows = table.find_all('tr')
        for row in rows[1:]:  # Skip header row
            cols = row.find_all('td')
            if len(cols) >= 7:
                country_img = cols[0].find('img')
                player_link = cols[0].find('a')
                team_img = cols[1].find('img')  # Find team image
                
                player = {
                    'country': country_img['alt'] if country_img else 'Unknown',
                    'name': player_link.text.strip() if player_link else 'Unknown',
                    'player_url': urljoin(base_url, player_link['href']) if player_link else None,
                    'team': team_img['alt'] if team_img else 'Unknown',  # Get team name
                    'maps': cols[2].text.strip(),
                    'rounds': cols[3].text.strip(),
                    'kd_diff': cols[4].text.strip(),
                    'kd': cols[5].text.strip(),
                    'rating': cols[6].text.strip()
                }
                players.append(player)
    
    return players

def get_next_page_url(html, base_url):
    soup = BeautifulSoup(html, 'html.parser')
    next_button = soup.find('a', class_='pagination-next')
    if next_button and 'disabled' not in next_button.get('class', []):
        return urljoin(base_url, next_button['href'])
    return None

def scrape_player_stats(base_url):
    all_players = []
    current_url = base_url
    page_number = 1
    
    while current_url:
        logging.info(f"Scraping page {page_number}: {current_url}")
        html = fetch_page(current_url)
        if html:
            players = parse_player_stats(html, base_url)
            all_players.extend(players)
            
            current_url = get_next_page_url(html, base_url)
            if current_url:
                time.sleep(random.uniform(3, 7))  # Random delay between page requests
                page_number += 1
        else:
            logging.error(f"Failed to fetch page {page_number}. Stopping.")
            break
    
    return all_players

def write_to_csv(data, filename):
    if not data:
        logging.warning("No data to write to CSV")
        return

    fieldnames = ['country', 'name', 'player_url', 'team', 'maps', 'rounds', 'kd_diff', 'kd', 'rating']

    with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for player in data:
            writer.writerow(player)

    logging.info(f"Data written to {filename}")

def main():
    base_url = 'https://www.hltv.org/stats/players'
    players = scrape_player_stats(base_url)
    
    if players:
        write_to_csv(players, 'hltv_player_stats.csv')
        logging.info(f"Successfully scraped data for {len(players)} players.")
    else:
        logging.error("No player data collected. Check if the scraping was successful.")

if __name__ == '__main__':
    main()