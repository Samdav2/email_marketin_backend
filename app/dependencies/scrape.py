import requests
from bs4 import BeautifulSoup
from pydantic import HttpUrl
from html.parser import HTMLParser

class Scraper:
    def __init__(self, url: HttpUrl):
        response = requests.get(str(url))
        self.scrape_content = BeautifulSoup(response.text, "html.parser")