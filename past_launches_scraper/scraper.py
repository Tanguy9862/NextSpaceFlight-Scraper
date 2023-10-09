from bs4 import BeautifulSoup
from time import sleep
from tqdm import tqdm
import csv
import logging
import os
import pandas as pd
import re
import requests

FORMATS = ["%a %b %d, %Y", "%a %b %d, %Y %H:%M UTC", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
MAX_RETRIES = 5
TIME_SLEEP = 2
PATH_TO_EXPORT = 'data'
DATA_FILENAME = "past_launches_data.csv"
SCRIPT_NAME = 'Past_Launches_Scraper'
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}
logging.basicConfig(level=logging.INFO)


def convert_to_date(date_str):
    for date_format in FORMATS:
        try:
            return pd.to_datetime(date_str, format=date_format)
        except ValueError:
            pass
    return None


def scrape_past_launches_data():

    def make_soup(url):
        retry_count = 0
        progressive_sleep = 2
        while retry_count < MAX_RETRIES:
            try:
                response = requests.get(url, headers=headers)
                break
            except requests.ConnectionError as e:
                retry_count += 1
                logging.info(f'{e} on page {i}')
                logging.info(f'Retrying.. (Attempt {retry_count})')
                sleep(progressive_sleep)
                progressive_sleep **= 2
        else:
            return None
        return BeautifulSoup(response.text, 'html.parser')

    try:
        df = pd.read_csv(f'{PATH_TO_EXPORT}/{DATA_FILENAME}')
    except FileNotFoundError:
        df = pd.DataFrame()
    else:
        df = df.sort_values(by='Date')
        last_date = convert_to_date(df.iloc[-1]['Date'])

    data = []
    i = 1
    stop_all = False
    previous_len_cards = 0

    while True:
        sleep(TIME_SLEEP)
        if not stop_all:
            logging.info(f'{SCRIPT_NAME} - Scrapping Page {i}..')
            soup = make_soup(f'https://nextspaceflight.com/launches/past/?page={i}&search=')
            if soup:
                all_cards = soup.find_all('div', class_='mdl-cell mdl-cell--6-col')

                for idx, card in tqdm(enumerate(all_cards), total=len(all_cards)):
                    date_location = card.find_next('div', class_='mdl-card__supporting-text').text.splitlines()
                    date_location = [e.strip() for e in date_location if e.strip()]
                    date = convert_to_date(date_location[0])

                    if not df.empty:
                        # Check if the current date is the same as the last date in the scraped data
                        if date == last_date:
                            stop_all = True
                            break

                    # Check if the current page is the same as previous page: the goal is to stop at the last page thus to not
                    # have an infinite scraping
                    if len(data) >= 30:
                        previous_page_first_card_date = data[len(data) - previous_len_cards]['Date']

                        if previous_page_first_card_date == date:
                            stop_all = True
                            break

                    organisation = card.span.text.strip()
                    rocket = card.find('h5', class_='header-style').text.strip()
                    location = date_location[-1]
                    style_content = card.style.text

                    default_image_link = 'https://storage.googleapis.com/nextspaceflight/media/rockets/default.jpg'
                    regex_image_link = re.search(r'url\((.*?)\)', style_content).group(1)
                    image_link = regex_image_link if regex_image_link != default_image_link else None

                    launch_number = re.search(r'\.launch\.a(\d+)', style_content).group(1)
                    details_url = f'https://nextspaceflight.com/launches/details/{launch_number}'
                    details_soup = make_soup(details_url)

                    if details_soup:
                        rocket_content = details_soup.find_all('div', class_='mdl-cell mdl-cell--6-col-desktop mdl-cell--12-col-tablet')
                        mission_status = details_soup.find('h6', class_='rcorners status').text.strip()

                        regex_status = re.compile(r'(?i)Status:\s*(\w+)')
                        regex_price = re.compile(r'(?i)Price:\s*\$([\d.]+) million')
                        status, price = None, None

                        for element in rocket_content:
                            match_status = regex_status.search(element.string)
                            match_price = regex_price.search(element.string)
                            if match_status:
                                status = match_status.group(1)

                            if match_price:
                                price = match_price.group(1)

                    data.append(
                        {
                            'Organisation': organisation,
                            'Detail': rocket,
                            'Location': location,
                            'Date': date,
                            'Image_Link': image_link,
                            'Mission_Status': details_soup and mission_status,
                            'Rocket_Status': details_soup and status,
                            'Price': details_soup and price
                        }
                    )

                    previous_len_cards = len(all_cards)

            i += 1
        else:
            break

    # Export to .csv format:
    if data:
        has_previous_file = os.path.exists(f'{PATH_TO_EXPORT}/{DATA_FILENAME}')
        with open(f'{PATH_TO_EXPORT}/{DATA_FILENAME}', mode='a', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=data[0].keys())
            if not has_previous_file:
                writer.writeheader()

            for row in tqdm(data, total=len(data), desc='[+] Exporting data to .csv'):
                writer.writerow(row)

    return logging.info(f'{SCRIPT_NAME} - {DATA_FILENAME} updated!')
