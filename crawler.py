import requests
import time
import re
import urllib.robotparser
import validators
import random
from bs4 import BeautifulSoup
from selenium import webdriver
import threading
from concurrent.futures import ThreadPoolExecutor
from selenium.common.exceptions import TimeoutException

links = [
    "https://community.vtex.com",
    "https://community.shopify.com",
    "https://comunidade.nuvemshop.com.br",
    "https://comunidade.nubank.com.br"
]

threadLock = threading.Lock()
global_counter = 0
rp = urllib.robotparser.RobotFileParser()
visited_links = []
total_links = 100

def get_robots_txt(url):
    return requests.get(f"{url}/robots.txt").text

def get_robots_url(url):
    return (f"{url}/robots.txt")

def verify_link_structure(link):
    if link != None and link:
        if 'javascript:void(0);' in link or 'None' in link or not rp.can_fetch('*', link):
            return False
        else:
            return True
    else:
        return False

def validate_link(link, base_link, heuristic):
    global rp
    valid_structure = verify_link_structure(link)
    if heuristic == True and valid_structure:
        print(heuristic)
        heuristic_words = ['/topic/','/c/','/t/','/question/']
        for element in heuristic_words:
            if element in link:
               return True
        random.seed(1)
        return random.random() >= 0.9
    else:
        return valid_structure     
    
def get_site_content(link, base_link, delay, heuristic):
    global global_counter, visited_links
    if delay != None:
        time.sleep(delay)
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.headless = True
    options.add_argument("--no-sandbox")
    options.page_load_strategy = 'eager'
    driver = webdriver.Chrome(options=options)
    try:
        driver.get(link)
        time.sleep(5)
        soup = BeautifulSoup(driver.page_source, "html.parser")
        with threadLock:
            global_counter += 1
            with open("links7.txt", "a") as myfile:
                myfile.write(link + '\n')
            print(global_counter)
        result = soup.findAll('a')
        driver.close()
        links = []
        for link in result:
            link = link.get('href')
            if not 'http' in str(link):
                link = base_link + str(link)
            if validate_link(link, base_link, heuristic) and link not in visited_links and validators.url(link):
                links.append(link)
    except TimeoutException:
        print('timeout ', link)
    return links

def links_base(base_link, rp, heuristic):
    global global_counter, visited_links
    delay = rp.crawl_delay("*")
    if heuristic == 'bfs':
        links = get_site_content(base_link, base_link, delay, False)
    else:
        links = get_site_content(base_link, base_link, delay, True)
    visited_links.append(base_link)
    while links != [] and global_counter < total_links:
        print(global_counter)
        if heuristic == 'bfs':
            links_results = set_up_threads(links, base_link, delay, False)
        else:
            links_results = set_up_threads(links, base_link, delay, True)
        for link in links:
            visited_links.append(link)
        links = []
        counter = 0
        for link_array in links_results:
            for link in link_array:
                if counter + global_counter >= total_links:
                    break
                else:
                    if not link in visited_links:
                        links.append(link)
                        counter += 1

def set_up_threads(links, base_link, delay, heuristic):
    base_links = []
    delays = []
    heuristics = []
    for link in links:
         base_links.append(base_link)
         delays.append(delay)
         heuristics.append(heuristic)
    with ThreadPoolExecutor(max_workers=10) as executor:
        return executor.map(get_site_content,  
                            links,
                            base_links,
                            delays,
                            heuristics,
                            timeout = 30)

def main():
    global global_counter
    for link in links:
        rp.set_url(get_robots_url(link))
        rp.read()
        links_base(link, rp, 'heuristic')
        with threadLock:
            global_counter = 0
        links_base(link, rp, 'bfs')
        with threadLock:
            global_counter = 0
main()