import logging
import pandas as pd
import re
from time import sleep
from tqdm import tqdm

from .config import CONFIG, LocalConfig, AWSConfig, GCPConfig
from past_launches_scraper.utils.data_manager import (
    load_existing_data,
    export_data_to_local,
    export_data_to_s3,
    export_data_to_cloud_storage
)
from past_launches_scraper.utils.generals import make_soup, convert_to_date, clean_past_launches_data

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)


def scrape_past_launches_data():

    df_initial, last_date = load_existing_data() or (pd.DataFrame(), None)
    data = []
    i = 1
    stop_all = False
    previous_len_cards = 0

    while True:
        sleep(CONFIG.TIME_SLEEP)
        if not stop_all:
            logging.info(f'[+] Scrapping Page {i}..')
            soup = make_soup(f'{CONFIG.BASE_URL_PAST_LAUNCH}{i}&search=', page_number=i)
            if soup:
                all_cards = soup.find_all('div', class_='mdl-cell mdl-cell--6-col')

                for idx, card in tqdm(enumerate(all_cards), total=len(all_cards)):
                    date_location = card.find_next('div', class_='mdl-card__supporting-text').text.splitlines()
                    date_location = [e.strip() for e in date_location if e.strip()]
                    date = convert_to_date(date_location[0])

                    # Check if the current date is the same as the last date in the scraped data
                    if last_date and last_date == date:
                        tqdm.write(
                            f"[!] No new data to scrape. Dataset is up to date. Last scraped date: {last_date}.")
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
                    details_soup = make_soup(details_url, page_number=i)

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

    # Export to .csv based on configured environment:
    if data:

        new_data_df = clean_past_launches_data(pd.DataFrame(data))
        df_final = df_initial._append(new_data_df, ignore_index=True)

        if isinstance(CONFIG, LocalConfig):
            export_data_to_local(df_final)
        elif isinstance(CONFIG, AWSConfig):
            export_data_to_s3(df_final)
        elif isinstance(CONFIG, GCPConfig):
            export_data_to_cloud_storage(df_final)
        else:
            raise RuntimeError(
                f"Invalid CONFIG detected. CONFIG must be an instance of either LocalConfig, AWSConfig, or GCPConfig. "
                f"Current CONFIG: {type(CONFIG).__name__}"
            )

        return df_final
