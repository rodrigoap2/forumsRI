import requests
import time
import re
import urllib.robotparser
import validators
from bs4 import BeautifulSoup
from selenium import webdriver
import threading

links = [
    "https://community.vtex.com"
]

threadLock = threading.Lock()
global_counter = 0
rp = urllib.robotparser.RobotFileParser()

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

def validate_link(link, base_link, rp):
    if link != None and link:
        if 'javascript:void(0);' in link or 'None' in link or not rp.can_fetch('*', link):
            return False
        else:
            return True
    else:
        return False

def get_site_content(link, delay):
    global global_counter
    if delay != None:
        time.sleep(delay)
    driver = webdriver.Chrome()
    driver.get(link)
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, "html.parser")
    with threadLock:
        global_counter += 1
    result = soup.findAll('a')
    driver.close()
    return result

def links_bfs(base_link, rp):
    global global_counter
    delay = rp.crawl_delay("*")
    a_tags = get_site_content(base_link, delay)
    links = []
    visited_links = []
    visited_links.append(base_link)
    for link in a_tags:
        link = link.get('href')
        if not 'http' in str(link):
            link = base_link + str(link)
        if validate_link(link, base_link, rp) and link not in visited_links:
            links.append(link)
    while links != [] and global_counter < 1000:
        print(global_counter)
        if validators.url(links[0]) and not links[0] in visited_links:
            actual_links = get_site_content(links[0], delay)
            visited_links.append(links[0])
            links.pop(0)
            for link in actual_links:
                link = link.get('href')
                if not 'http' in str(link):
                    link = base_link + str(link)
                if validate_link(link, base_link, rp) and link not in visited_links:
                    links.append(link)
        else: 
            links.pop(0)

    return visited_links
    

def main():
    for link in links:
        robot_informations = parse_robots_txt(get_robots_txt(link))
        rp.set_url(get_robots_url(link))
        rp.read()
        #sitemaps = require_sitemaps(robot_informations["Sitemap"], robot_informations["Crawl-delay"])
        # for sitemap in sitemaps:
        #     get_sitemap_links(sitemap[0], link_counter)
        link_counter = 0
        site_links = links_bfs(link, rp)
        print(site_links)
main()