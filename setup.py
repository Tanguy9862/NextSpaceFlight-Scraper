from setuptools import setup, find_packages

setup(
    name='Past_Launches_Space_Scraper',
    version='0.1',
    packages=find_packages(),
    install_requires=[
        'bs4',
        'requests',
        'pandas',
        'tqdm'
    ]
)
