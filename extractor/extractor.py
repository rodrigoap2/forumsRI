import time
from bs4 import BeautifulSoup
from selenium import webdriver
import lxml.html

def generate_xpath(element):
    components = []
    child = element if element.name else element.parent
    for parent in child.parents:  # type: bs4.element.Tag
        siblings = parent.find_all(child.name, recursive=False)
        components.append(
            child.name if 1 == len(siblings) else '%s[%d]' % (
                child.name,
                next(i for i, s in enumerate(siblings, 1) if s is child)
                )
            )
        child = parent
    components.reverse()
    return '/%s' % '/'.join(components)

def extractor(link):
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.headless = True
    options.add_argument("--no-sandbox")
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "lxml")
    root = lxml.html.fromstring(driver.page_source)
    if 'community.shopify' in link:
        result = soup.findAll('div',  {"class": ["lia-message-view-forum-message", "lia-quilt-row-topic-header"]})
    else: 
        result = soup.findAll('article')
    for article in result:
        for div in article.findAll('div', recursive=False):
            print(generate_xpath(div))
            print(driver.find_element_by_xpath(generate_xpath(div)).text)
        print()

if __name__ == "__main__":
    extractor('https://community.shopify.com/c/Tudo-sobre-a-Shopify/Pixel/td-p/1127667')