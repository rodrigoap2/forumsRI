from bs4 import BeautifulSoup
from selenium import webdriver
import time
import constants
import pandas as pd
from utils import get_parsed_phrase, get_parsed_vtex
from tqdm import tqdm

sites = [constants.VTEX]
site_name = ['vtex']

for name, site in zip(site_name, sites):
    
    bodies = {
        "text": [],
        "target": []
    }

    for i, pages in enumerate(site):
        for page in pages:
            options = webdriver.ChromeOptions()
            options.add_argument("--ignore-certificate-errors")
            options.add_argument("--incognito")
            options.headless = True
            options.add_argument("--no-sandbox")
            driver = webdriver.Chrome('./chromedriver', options=options)
            driver.get(page)
            time.sleep(5)
            soup = BeautifulSoup(driver.page_source, "html.parser")
            blacklist = [
                'style',
                'script'
            ]
            text_elements = [t for t in soup.find_all(
                text=True) if t.parent.name not in blacklist]
            text_elements = list(filter(lambda x: not (
                'render facet' in x or '\n' in x or '\xa0' in x), text_elements))
            driver.close()

            # print(text_elements)

            text = get_parsed_vtex(soup.find('title').text, text_elements)


            bodies["text"].append(text)
            bodies["target"].append(i)

    dataframe = pd.DataFrame(bodies)
    dataframe.to_csv(f'{name}.csv', index=False)

# options = webdriver.ChromeOptions()
# options.add_argument("--ignore-certificate-errors")
# options.add_argument("--incognito")
# options.headless = True
# options.add_argument("--no-sandbox")
# options.page_load_strategy = 'eager'
# driver = webdriver.Chrome(options=options)
# driver.get(link)
# time.sleep(5)
# soup = BeautifulSoup(driver.page_source, "html.parser")
# driver.close()
