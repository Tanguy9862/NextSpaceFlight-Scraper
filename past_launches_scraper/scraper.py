from bs4 import BeautifulSoup
from google.cloud import storage
from io import BytesIO
from time import sleep
from tqdm import tqdm
from past_launches_scraper.utils import read_csv_from_gcs, exists_on_cloud, clean_past_launches_data
import logging
import os
import pandas as pd
import re
import requests

FORMATS = ["%a %b %d, %Y", "%a %b %d, %Y %H:%M UTC", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
MAX_RETRIES = 5
TIME_SLEEP = 2
BUCKET_NAME = 'spacexploration_data'
BLOB_NAME = 'past_launches_data.csv'
SCRIPT_NAME = 'Past_Launches_Scraper'
headers = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}
logging.basicConfig(level=logging.INFO)

if os.path.exists('spacexploration-keys.json'):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'spacexploration-keys.json'


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

    if exists_on_cloud(BUCKET_NAME, BLOB_NAME):
        df = read_csv_from_gcs(BUCKET_NAME, BLOB_NAME).sort_values(by='Date')
        last_date = convert_to_date(df.iloc[-1]['Date'])
    else:
        df = pd.DataFrame()

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

    # Export to .csv on GCS:
    if data:
        logging.info(f'{SCRIPT_NAME} - {BLOB_NAME} Adding new data..')

        # Merge df_initial with new_data:
        new_data = pd.DataFrame(data)
        new_data = clean_past_launches_data(new_data)
        df_initial = (exists_on_cloud(BUCKET_NAME, BLOB_NAME) or pd.DataFrame()) and read_csv_from_gcs(BUCKET_NAME, BLOB_NAME)
        df_final = df_initial._append(new_data, ignore_index=True)

        # Upload df_final on GCS:
        storage_client = storage.Client()
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(BLOB_NAME)
        byte_stream = BytesIO()
        df_final.to_csv(byte_stream, index=False)
        byte_stream.seek(0)
        blob.upload_from_file(byte_stream, content_type='text/csv')

    return logging.info(f'{SCRIPT_NAME} - {BLOB_NAME} updated!')
