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

def scrape_page(url, outputfile):
    
    response = requests.get(url)

    if response.status_code == 200:
        print(f'Successfully fetched the wepage: {url}')

        soup = BeautifulSoup(response.text, "html.parser")

        match_cards = soup.find_all("span", class_="MatchCard")
        with open(outputfile, 'a', encoding="utf-8") as file:
            for match_card in match_cards:
                span_html = match_card.prettify()
                match_event_line = match_card.find_next("div", class_="MatchEventLine")
                if match_event_line:
                    div_html = match_event_line.prettify()
                else:
                    div_html = "No matching <div class='MatchEventLine'> found."

                
                span_html = "\n".join(line.lstrip() for line in span_html.split("\n"))
                div_html = "\n".join(line.lstrip() for line in div_html.split("\n"))

                file.write("Extracted <span class='MatchCard'>:\n")
                file.write(span_html + '\n')
                file.write("\nExtracted <div class='MatchEventLine'>:\n")
                file.write(div_html + "\n")
                file.write("-" * 50 + "\n")
    

    else:
        print(f"Failed to fetch the webpage: {url}. Status Code: {response.status_code}")


def main():
    base_url = 'https://www.cagematch.net/?id=2&nr=86&page=4&constellationType=Singles&s={offset}'

    output_dir = "./data/"
    os.makedirs(output_dir, exist_ok=True)

    output_file = os.path.join(output_dir, "extracted_html.txt")

    if os.path.exists(output_file):
        os.remove(output_file)

    for page in range(20):
        offset = page * 100
        url = base_url.format(offset=offset)
        scrape_page(url, output_file)

    print(f"Extracted data saved to {output_file}")
    

if __name__ == "__main__":
    main()