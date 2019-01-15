# Scrapes details of media files published by Faraday Institute
# See https://twitter.com/SubtleEngine/status/1082577793886683137

import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def fetch_page(params, urls):
    url = "https://www.sms.cam.ac.uk/institution/FARADAY"
    r = requests.get(url, params=params)
    soup = BeautifulSoup(r.text, "html.parser")
    pages = len(soup.find("div", class_="paginate").find_all("a"))
    items = soup.find_all("div", class_="listTabPanelRow")
    urls = [item.find("h4", class_="itemTitle").find("a").attrs["href"] for item in items]
    return pages, urls

def fetch_pages():
    params = {"mediaOffset": 0, "mediaMax": 100}
    urls = []
    pages, urls = fetch_page(params, urls)
    for page in range(1, pages):
        params["mediaOffset"] = page*100
        pages, new_urls = fetch_page(params, urls)
        urls = urls + new_urls
    return urls

def fetch_details(urls):
    details_all = []
    for url in urls:
        r = requests.get("https://www.sms.cam.ac.uk" + url)
        soup = BeautifulSoup(r.text, "html.parser")
        try: # Bit hacky
            title = soup.find("meta", itemprop="name").attrs["content"].strip()
            description = soup.find("meta", itemprop="description").attrs["content"].strip()
            url = soup.find("meta", itemprop="contentURL").attrs["content"][6:].strip()
            keywords = "; ".join(sorted([k.get_text().strip().lower() for k in soup.find_all("a", href=re.compile("keyword"))]))
        except AttributeError as e:
            title = "Not found"
            description = "Not found"
            url = "Not found"
            keywords = "Not found"
        details = {"title": title, "description": description, "url": url, "keywords": keywords}
        details_all.append(details)
    return details_all

urls = fetch_pages()
details = fetch_details(urls)
details = pd.DataFrame(details)
details = details[details["title"] != "Not found"]
details = details[["title", "description", "keywords", "url"]].to_csv("faraday-media.csv", index=False)









