from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path.cwd() / ".env"
load_dotenv(dotenv_path=env_path)
ENV = os.getenv("ENV", "local")
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = 'spacexploration-gcp-bucket-access.json' or None


class BaseConfig:
    SCRIPT_NAME = 'nsf_past_launches_space_scraper'
    FORMATS = ["%a %b %d, %Y", "%a %b %d, %Y %H:%M UTC", "%Y-%m-%d", "%Y-%m-%d %H:%M:%S"]
    MAX_RETRIES = 5
    TIME_SLEEP = 2
    HEADERS = {"User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:108.0) Gecko/20100101 Firefox/108.0"}
    BASE_URL_PAST_LAUNCH = 'https://nextspaceflight.com/launches/past/?page='
    DATA_EXPORT_FILENAME = "nsf_past_launches.csv"


class LocalConfig(BaseConfig):
    DATA_DIR_NAME = 'data'


class AWSConfig(BaseConfig):
    BUCKET_NAME = "app-space-exploration-bucket"


class GCPConfig(BaseConfig):
    BUCKET_NAME = 'space-exploration-bucket-test'


def get_config():
    if ENV == "local":
        return LocalConfig()
    elif ENV == 'aws':
        return AWSConfig()
    elif ENV == 'gcp':
        return GCPConfig()
    return LocalConfig()


CONFIG = get_config()
