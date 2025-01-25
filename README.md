# NextSpaceFlight-Scrapper

**NextSpaceFlight-Scraper** is a Python module for scraping past space launch data from the [Next Spaceflight](https://nextspaceflight.com) website. It allows you to customize the environment (local, AWS, or GCP) and configure storage locations as needed.

## Installation

1. Clone the repository and install dependencies:
   ```bash
   git clone https://github.com/Tanguy9862/NextSpaceFlight-Scraper.git
   pip install -r requirements.txt
   ```

2. Configure the environment:
   - Create a `.env` file in the root directory to specify the environment (default: `local`):
     ```plaintext
     ENV=local
     ```
   - Supported environments:
     - `local`: Saves data to the `data/` directory.
     - `aws`: Uploads data to an AWS S3 bucket. Set the bucket name in `AWSConfig`.
     - `gcp`: Uploads data to a GCP Storage bucket. Set the bucket name in `GCPConfig`.

3. Modify the `config.py` file if needed:
   - Customize the storage location or other scraper settings in the appropriate class (`LocalConfig`, `AWSConfig`, or `GCPConfig`).
   - Example for AWS:
     ```python
     class AWSConfig(BaseConfig):
         BUCKET_NAME = "your-custom-aws-bucket-name"
     ```
   - Example for GCP:
     ```python
     class GCPConfig(BaseConfig):
         BUCKET_NAME = "your-custom-gcp-bucket-name"
     ```
     
## Usage

To use the scraper, call the `scrape_past_launches_data()` function in your script. Example:

```python
from past_launches_scraper.scraper import scrape_past_launches_data

# Run the scraper
scrape_past_launches_data()
```

Depending on the configured environment:
- **Local environment**: Data will be saved (or updated) to the `data/nsf_past_launches.csv` file.
- **AWS environment**: Data will be uploaded to the S3 bucket specified in `AWSConfig.BUCKET_NAME`.
- **GCP environment**: Data will be uploaded to the Google Cloud Storage bucket specified in `GCPConfig.BUCKET_NAME`.

## Integration Example

This module is used in [Space-App](https://github.com/Tanguy9862/Space-App), a Dash app deployed on GCP. The scraper runs as part of a Cloud Run function triggered periodically (every 3 hours). Scraped data is stored in a GCP Storage bucket and fetched by the Dash app for visualization.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Related Projects

- [Space-App](https://github.com/Tanguy9862/Space-App)
