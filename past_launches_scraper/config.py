from pathlib import Path
from dotenv import load_dotenv
import os

env_path = Path.cwd() / ".env"
load_dotenv(dotenv_path=env_path)


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


class LambdaConfig(BaseConfig):
    BUCKET_NAME = "app-space-exploration-bucket"


ENV = os.getenv("ENV", "local")
CONFIG = LocalConfig() if ENV == "local" else LambdaConfig()
