# NextSpaceFlight-Scrapper

## Overview

This Python package is designed to scrape historical space launch data. It complements the [Space-App](https://github.com/Tanguy9862/Space-App) project by providing the data backbone for various visualizations and analyses.

## Features

- **Historical Data**: Scrapes comprehensive historical data on space launches, including the launch vehicle, launch site, mission objectives, outcomes, etc.
- **Data Transformation**: Transforms the scraped data into a JSON format for easy consumption.
- **Time-Series Analysis**: The data is structured to facilitate time-series analysis, allowing for trend identification and predictive modeling.
- **Error Handling**: Robust error handling to ensure data integrity.
- **Logging**: Detailed logging for debugging and monitoring.

## Installation

To install this package, run:

```bash
pip install git+https://github.com/Tanguy9862/NextSpaceFlight-Scrapper.git
```

## Usage

After installation, you can import the package and use the `scrape_past_launches_data()` function to scrape the data.

```python
from next_spaceflight_scrapper import scraper

# Scrape historical launch data
scraper.scrape_past_launches_data()
```

## Dependencies

- Python 3.x
- BeautifulSoup
- Requests
- Pandas

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Space-App](https://github.com/Tanguy9862/Space-App)
- [Wikipedia_Space_Scraper](https://github.com/Tanguy9862/Wikipedia_Space_Scraper)
- [Next-Launch-Scraper](https://github.com/Tanguy9862/Next-Launch-Scraper)
