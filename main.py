import requests
import time
import re
import urllib.robotparser
import validators
from bs4 import BeautifulSoup
from selenium import webdriver
import threading
from concurrent.futures import ThreadPoolExecutor

links = [
    "https://comunidade.nubank.com.br",
    "https://comunidade.nuvemshop.com.br",
    "https://community.shopify.com/",
    "https://community.vtex.com"
]

threadLock = threading.Lock()
global_counter = 0
rp = urllib.robotparser.RobotFileParser()
visited_links = []

def get_robots_txt(url):
    return requests.get(f"{url}/robots.txt").text

def get_robots_url(url):
    return (f"{url}/robots.txt")

def parse_robots_txt(html):
    lines = html.split('\n')
    informations = {"Disallow": [], "Sitemap": "", "Crawl-delay": 0, "Allow": []}
    actual_user_agent = ""
    for line in lines:
        if ":" in line:
            line_infos = line.split(": ")
            if "sitemap" in line_infos[0].lower():
                informations["Sitemap"] = "".join(line_infos[1:]).split(" ")[0] #Getting the sitemap
            elif "user-agent" in line_infos[0].lower():
                actual_user_agent = "".join(line_infos[1:]).split(" ")[0]
            elif "disallow" in line_infos[0].lower():
                if(actual_user_agent == "*"):
                    informations["Disallow"].append("".join(line_infos[1:]).split(" ")[0])
            elif "crawl-delay" in line_infos[0].lower():
                if(actual_user_agent == "*"):
                    informations["Crawl-delay"] = int("".join(line_infos[1:]).split(" ")[0])
            elif "allow" in line_infos[0].lower():
                if(actual_user_agent == "*"):
                    informations["Allow"].append("".join(line_infos[1:]).split(" ")[0])
    return informations

def validate_link(link, base_link):
    global rp
    if link != None and link:
        if 'javascript:void(0);' in link or 'None' in link or not rp.can_fetch('*', link):
            return False
        else:
            return True
    else:
        return False

def get_site_content(link, base_link, delay):
    global global_counter, visited_links
    if delay != None:
        time.sleep(delay)
    options = webdriver.ChromeOptions()
    options.add_argument("--ignore-certificate-errors")
    options.add_argument("--incognito")
    options.headless = True
    options.add_argument("--no-sandbox")
    driver = webdriver.Chrome(options=options)
    driver.get(link)
    time.sleep(5)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    with threadLock:
        global_counter += 1
        with open("links2.txt", "a") as myfile:
            myfile.write(link + '\n')
        print(global_counter)
    result = soup.findAll('a')
    driver.close()
    links = []
    for link in result:
        link = link.get('href')
        if not 'http' in str(link):
            link = base_link + str(link)
        if validate_link(link, base_link) and link not in visited_links and validators.url(link):
            links.append(link)
    return links

def links_bfs(base_link, rp):
    global global_counter, visited_links
    delay = rp.crawl_delay("*")
    links = get_site_content(base_link, base_link, delay)
    visited_links.append(base_link)
    while links != [] and global_counter < 1000:
        print(global_counter)
        links_results = set_up_threads(links, base_link, delay)
        for link in links:
            visited_links.append(link)
        links = []
        counter = 0
        for link_array in links_results:
            for link in link_array:
                if counter + global_counter >= 1000:
                    break
                else:
                    if not link in visited_links:
                        links.append(link)
                        counter += 1
        
    return visited_links

def set_up_threads(links, base_link, delay):
    base_links = []
    delays = []
    for link in links:
         base_links.append(base_link)
         delays.append(delay)
    with ThreadPoolExecutor(max_workers=10) as executor:
        return executor.map(get_site_content,  
                            links,
                            base_links,
                            delays,
                            timeout = 30)

def main():
    for link in links:
        robot_informations = parse_robots_txt(get_robots_txt(link))
        rp.set_url(get_robots_url(link))
        rp.read()
        #sitemaps = require_sitemaps(robot_informations["Sitemap"], robot_informations["Crawl-delay"])
        # for sitemap in sitemaps:
        #     get_sitemap_links(sitemap[0], link_counter)
        site_links = links_bfs(link, rp)
        print(site_links)
main()