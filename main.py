import requests
import time
from bs4 import BeautifulSoup

links = [
        "https://community.shopify.com/",
        "https://community.spotify.com/",
        "https://community.acer.com/"
        ]

def get_robots_txt(url):
    return requests.get(f"{url}robots.txt").text

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

def require_sitemaps(sitemap, delay):
    if delay > 0:
        time.sleep(delay)
    sitemaps_dict = {}

    request = requests.get(sitemap)
    xml = request.text

    soup = BeautifulSoup(xml, "html.parser")
    sitemap_tags = soup.find_all("sitemap")

    while sitemap_tags != [] and not(sitemap_tags[0].findNext("loc").text in sitemaps_dict):
        site = sitemap_tags[0].findNext("loc").text
        sitemaps_dict[site] = sitemap_tags[0].findNext("lastmod").text
        if delay > 0:
            time.sleep(delay)
    
        request = requests.get(site)
        xml = request.text
        soup = BeautifulSoup(xml, "html.parser")
        sitemaps = soup.find_all("sitemap")
        sitemap_tags.pop(0)
        for element in sitemaps:
            sitemap_tags.append(element)
        
    return sitemaps_dict

def main():
    for link in links:
        robot_informations = parse_robots_txt(get_robots_txt(link))
        sitemaps = require_sitemaps(robot_informations["Sitemap"], robot_informations["Crawl-delay"])

main()