# NextSpaceFlight-Scrapper

## Overview

This Python package is designed to scrape historical space launch data from NextSpaceFlight.com and store it in Google Cloud Storage. It complements the [Space-App](https://github.com/Tanguy9862/Space-App) project by providing the data backbone for various visualizations and analyses.

## Features

- **Source**: Scrapes comprehensive historical data from NextSpaceFlight.com.
- **Historical Data**: Gathers detailed information on past space launches.
- **Data Transformation**: Transforms the scraped data into a CSV format for easy consumption.
- **Google Cloud Storage**: Automatically uploads the scraped data to Google Cloud Storage.
- **Data Update**: Checks for existing data in Google Cloud Storage and appends new data.
- **Error Handling**: Robust error handling to ensure data integrity.
- **Logging**: Detailed logging for debugging and monitoring.

## Installation

To install this package, run:

```bash
pip install git+https://github.com/Tanguy9862/NextSpaceFlight-Scrapper.git
```

## Usage

After installation, you can import the package and use the `scrape_past_launches_data()` function to scrape and update the data.

```python
from next_spaceflight_scrapper import scraper

# Scrape and update historical launch data
scraper.scrape_past_launches_data()
```

## Dependencies

- Python 3.x
- BeautifulSoup
- Requests
- Pandas
- Google Cloud Storage

## Authentication

To access Google Cloud Storage, you'll need a JSON file containing your GCS authentication keys. Place this file in the `past_launches_scrapper` directory and name it `spacexploration-keys.json`.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Space-App](https://github.com/Tanguy9862/Space-App)
