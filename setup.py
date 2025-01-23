from setuptools import setup, find_packages

setup(
    name='nsf_past_launches_space_scraper',
    version='0.2',
    packages=find_packages(),
    install_requires=[
        'bs4',
        'requests',
        'pandas',
        'tqdm',
        'iso3166',
        'numpy',
        'python-dotenv',
        'boto3',
        'google-cloud-storage'
    ]
)
