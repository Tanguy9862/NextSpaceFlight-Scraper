import os
import boto3
import pandas as pd
import logging
from pathlib import Path
from io import StringIO

from ..config import CONFIG, LocalConfig, LambdaConfig
from ..utils.generals import get_most_recent_date


def get_local_export_path():

    # Set export directory and file path, creating the directory if needed.
    current_dir = Path.cwd()
    export_dir = current_dir / CONFIG.DATA_DIR_NAME
    export_dir.mkdir(parents=True, exist_ok=True)
    return export_dir / CONFIG.DATA_EXPORT_FILENAME


def load_existing_data():

    if isinstance(CONFIG, LocalConfig):
        logging.info(f'[LOCAL ENV] -> Trying to load data from: {CONFIG.DATA_DIR_NAME}/{CONFIG.DATA_EXPORT_FILENAME}')
        filepath = get_local_export_path()

        if os.path.exists(filepath):
            df = pd.read_csv(filepath)

            try:
                last_date = get_most_recent_date(df)
                logging.info(f'[+] Previous data file found. Last date in the file: {last_date}')
                return df, last_date
            except ValueError as e:
                logging.error(f"[!] Failed to retrieve the most recent date: {e}")
                raise

        logging.warning(f'[+] No existing data file detected at `{filepath}`. Scraping all data from scratch.')
        return False

    elif isinstance(CONFIG, LambdaConfig):
        logging.info(
            f'[AWS ENV] -> Attempting to load data file from Bucket: {CONFIG.BUCKET_NAME}, '
            f'Key: {CONFIG.DATA_EXPORT_FILENAME}')
        s3 = boto3.client('s3')
        try:
            response = s3.get_object(Bucket=CONFIG.BUCKET_NAME, Key=CONFIG.DATA_EXPORT_FILENAME)
            csv_content = response['Body'].read().decode('utf-8')
            df = pd.read_csv(StringIO(csv_content))
            last_date = get_most_recent_date(df)
            logging.info(f'[+] Data file successfully loaded from S3. Last date in the file: {last_date}')
            return df, last_date
        except ValueError as e:
            logging.error(f"[!] Failed to retrieve the most recent date: {e}")
            raise
        except s3.exceptions.NoSuchKey:
            logging.warning(f'[+] No data file found in S3 at Key: `{CONFIG.DATA_EXPORT_FILENAME}`. Scraping all data '
                            f'from scratch.')
            return False

    raise RuntimeError(
        f"Invalid CONFIG detected. CONFIG must be an instance of either LocalConfig or LambdaConfig. "
        f"Current CONFIG: {type(CONFIG).__name__}"
    )


def export_data_to_s3(updated_data: pd.DataFrame):
    """
    Export the updated data (DataFrame) to an S3 bucket as a CSV file.
    """
    try:
        logging.info(f'[+] Uploading updated data file to bucket {CONFIG.BUCKET_NAME} [..]')

        # Convert DataFrame to CSV
        csv_buffer = updated_data.to_csv(index=False).encode('utf-8')

        # Upload CSV to S3
        s3 = boto3.client('s3')
        s3.put_object(
            Bucket=CONFIG.BUCKET_NAME,
            Key=CONFIG.DATA_EXPORT_FILENAME,
            Body=csv_buffer,
            ContentType='text/csv'
        )
        logging.info(f'[+] DONE! Data successfully uploaded to {CONFIG.BUCKET_NAME}/{CONFIG.DATA_EXPORT_FILENAME}')
    except Exception as e:
        logging.warning(f'[!] Error uploading file to S3: {e}')


def export_data_to_local(updated_data: pd.DataFrame):
    """
    Export the updated data (DataFrame) to a local CSV file.
    """
    try:
        filepath = get_local_export_path()
        logging.info(f'[+] Saving updated data file locally to {filepath} [..]')

        # Export DataFrame to CSV
        updated_data.to_csv(filepath, index=False, encoding='utf-8')

        logging.info(f'[+] DONE! Data successfully saved to {filepath}')
    except Exception as e:
        logging.warning(f'[!] Error saving file locally: {e}')
