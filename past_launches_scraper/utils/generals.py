import requests
import logging
import pandas as pd
import numpy as np

from time import sleep
from bs4 import BeautifulSoup
from typing import Union
from iso3166 import countries

from ..config import CONFIG


def make_soup(url, page_number):
    retry_count = 0
    progressive_sleep = 2
    while retry_count < CONFIG.MAX_RETRIES:
        try:
            response = requests.get(url, headers=CONFIG.HEADERS)
            break
        except (requests.ConnectionError, TimeoutError) as e:
            retry_count += 1
            logging.info(f'{e} on page {page_number}')
            logging.info(f'Retrying.. (Attempt {retry_count})')
            sleep(progressive_sleep)
            progressive_sleep **= 2
    else:
        return None
    return BeautifulSoup(response.text, 'html.parser')


def get_most_recent_date(df: pd.DataFrame, date_column: str = 'Date') -> Union[pd.Timestamp, bool]:
    try:
        df[date_column] = pd.to_datetime(df[date_column])
        return df[date_column].max()
    except Exception as e:
        logging.error(f"Error while processing column `{date_column}`: {e}")
        raise ValueError(f"Failed to get the most recent date from column `{date_column}`.")


def clean_past_launches_data(df):
    df['Country'] = df.Location.str.rsplit(',').str[-1].str.strip()
    df.loc[(df.Country == "Russia"), "Country"] = "Russian Federation"
    df.loc[(df.Country == "New Mexico"), "Country"] = "USA"
    df.loc[(df.Country == "Yellow Sea"), "Country"] = "China"
    df.loc[(df.Country == "Shahrud Missile Test Site"), "Country"] = "Iran"
    df.loc[(df.Country == "Pacific Missile Range Facility"), "Country"] = "USA"
    df.loc[(df.Country == "Barents Sea"), "Country"] = "Russian Federation"
    df.loc[(df.Country == "Gran Canaria"), "Country"] = "USA"

    def get_country_name(x):
        if x != "IRN" and x != "PRK":
            try:
                return countries.get(x).alpha3
            except KeyError:
                return 'Unknown'
        else:
            return x

    df['country_code'] = df.Country.apply(lambda x: get_country_name(x))
    df.loc[df['Country'] == 'Iran', 'country_code'] = 'IRN'
    df.loc[df['Country'] == 'North Korea', 'country_code'] = 'PRK'

    # PRICE COL FORMAT:
    df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

    # MISSION_STATUS_BINARY:
    df['Mission_Status_Binary'] = np.where(df.Mission_Status != "Success", "Failure", "Success")

    # YEAR_LAUNCH:
    df['YEAR_LAUNCH'] = pd.DatetimeIndex(df['Date']).year

    return df


def convert_to_date(date_str):
    for date_format in CONFIG.FORMATS:
        try:
            return pd.to_datetime(date_str, format=date_format)
        except ValueError:
            pass
    return None
