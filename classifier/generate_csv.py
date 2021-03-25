import requests
from utils import get_parsed_body, preprocess_phrase, get_parsed_phrase
from bs4 import BeautifulSoup
import constants
import pandas as pd
from tqdm import tqdm

# Sem VTEX até agr pq falta o Selenium

sites = [constants.NUBANK, constants.NUVEM, constants.SHOPIFY]
site_name = ['nubank', 'nuvem', 'shopify']

for name, site in tqdm(zip(site_name, sites)):

    bodies = {
        "text": [],
        "target": []
    }

    for i, pages in enumerate(site):
        for page in pages:
            page = requests.get(page)
            soup = BeautifulSoup(page.content, 'html.parser')
            text = get_parsed_phrase(soup)
            bodies["text"].append(text)
            bodies["target"].append(i)

    dataframe = pd.DataFrame(bodies)
    dataframe.to_csv(f'{name}.csv', index=False)

