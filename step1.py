'''

filename: step1.py
author: Raul Pacheco
email: rpacheco5000@gmail.com
created: 2025-04-13
modified: 2025-04-13
description: Pulls and cleans data from Cagematch.com

'''

import os
import requests
from bs4 import BeautifulSoup
import time

# Constraints
BASE_URL = 'https://www.cagematch.net/?id=2&nr=86&page=4&constellationType=Singles&s={offset}'
OUTPUT_DIR = './data/'
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "extracted_matches.txt")
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
# Delay 2 seconds between requests to avoid rate limiting
DELAY = 2


def scrape_page(url):
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status() # Raises HTTPError for bad responses

        soup = BeautifulSoup(response.text, "html.parser")
        matches = []

        for match_card in soup.find_all("span", class_="MatchCard"):
            match_data = {
                'card': "\n".join(line.lstrip() for line in match_card.prettify().split("\n")),
                'event_line': None
            }

            event_line = match_card.find_next("div", class_="MatchEventLine")
            if event_line:
                match_data['event_line'] = "\n".join(line.lstrip() for line in event_line.prettify().split('\n'))
            
            matches.append(match_data)
        
        return matches

    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def save_matches(matches, output_file):
    with open(output_file, 'a', encoding="utf-8") as f:
        for match in matches:
            f.write("Extracted <span class = 'MatchCard'>:\n")
            f.write(match['card'] + "\n")

            if match['event_line']:
                f.write('\nExtracted <div class="MatchEventLine">:\n')
                f.write(match['event_line'] + "\n")
            else:
                f.write("\nNo matching <div class='MatchEventLine'> found.\n")
            
            f.write("-"*50+"\n")

def get_max_pages():
    """Dynamically determine the number of pages to scrape."""
    try:
        response = requests.get(BASE_URL.format(offset=0), headers=HEADERS)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")
        
        # Method 1: Look for pagination text (e.g., "Page 1 of 50")
        pagination_text = soup.find(string=lambda t: "Page" in t and "of" in t)
        if pagination_text:
            total_pages = int(pagination_text.split("of")[-1].strip())
            return total_pages
        
        # Method 2: Find the highest numbered page link
        page_links = soup.select("a[href*='s=']")
        if page_links:
            max_offset = 0
            for link in page_links:
                href = link.get('href', '')
                if 's=' in href:
                    offset = int(href.split('s=')[-1].split('&')[0])
                    max_offset = max(max_offset, offset)
            if max_offset > 0:
                return (max_offset // 100) + 1
        
        # Method 3: Check if there's a "Next" button but no more pages
        next_button = soup.find("a", text="Next")
        if not next_button:
            return 1  # Only one page exists
        
        # If all methods fail, default to a reasonable number
        print("Warning: Using conservative default of 20 pages")
        return 20
    
    except Exception as e:
        print(f"Error detecting pages: {e}")
        print("Defaulting to 20 pages")
        return 20    


def main():
    # Setup output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Clear previous output
    if os.path.exists(OUTPUT_FILE):
        os.remove(OUTPUT_FILE)

    # Get total pages dynamically
    total_pages = get_max_pages()
    print(f"Found {total_pages} pages to scrape.")

    # Scrape Each Page
    for page in range(total_pages):
        offset = page * 100
        url = BASE_URL.format(offset=offset)
        print(f"Scraping page {page + 1}/{total_pages}...")

        matches = scrape_page(url)
        if matches:
            save_matches(matches, OUTPUT_FILE)

        time.sleep(DELAY)

    print(f"Extracted data saved to {OUTPUT_FILE}")
    

if __name__ == "__main__":
    main()