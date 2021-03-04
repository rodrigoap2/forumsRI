import requests

links = ["https://comunidade.nubank.com.br/",
        "https://community.vtex.com/",
        "https://comunidade.nuvemshop.com.br/",
        "https://community.shopify.com/",
        "https://discussions.apple.com/",
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
            line_infos = line.split(":")
            if "sitemap" in line_infos[0].lower():
                informations["Sitemap"] = "".join(line_infos[1:]).split(" ")[1] #Getting the sitemap
                print(informations["Sitemap"])
            elif "user-agent" in line_infos[0].lower():
                actual_user_agent = "".join(line_infos[1:]).split(" ")[1]
            elif "disallow" in line_infos[0].lower():
                if(actual_user_agent == "*"):
                    informations["Disallow"].append("".join(line_infos[1:]).split(" ")[1])
            elif "crawl-delay" in line_infos[0].lower():
                if(actual_user_agent == "*"):
                    informations["Crawl-delay"] = int("".join(line_infos[1:]).split(" ")[1])
            elif "allow" in line_infos[0].lower():
                if(actual_user_agent == "*"):
                    informations["Allow"].append("".join(line_infos[1:]).split(" ")[1])
    return informations

def main():
    for link in links:
        robot_informations = parse_robots_txt(get_robots_txt(link))

main()