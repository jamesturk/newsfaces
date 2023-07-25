# Util Functions
import time
import requests
from urllib.parse import urlparse
import lxml.html
from wayback import WaybackClient, memento_url_data, WaybackSession
import itertools
import datetime
from crawlers.utils import make_request, parse_html, make_link_absolute, page_grab
import pytz
from nbc import get_nbc
from politico import politico_get_urls
from ap import get_urls_ap
from crawlers.crawler import Crawler, WaybackCrawler(Crawler)


class WashingtonPost(WaybackCrawler):
    def get_archive_urls(self, url, selectors):
        """
        Implement get_archive_urls here to override behavior
        """

class Fox(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.foxnews.com/politics"
        self.selector = ["article"]

class WashingtonTimes(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = 'https://www.washingtontimes.com/news/politics/'
        self.selector = ["article"]

class NBC(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url='https://www.nbcnews.com/politics/'
        self.selector =[]
    def get_archive_urls(self, url, selectors):
        """
        Implement get_archive_urls here to override behavior
        """
        return get_nbc(url, self.session)

class Politico(Crawler):
    def __init__(self):
        super().__init__()

    def crawl(self):
        """
        Implement crawl here to override behavior
        """
        return politico_get_urls()

class TheHill(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = 'https://thehill.com/policy/'
        self.selector = ['div.archive__item__content','h2.node__title.node-title']

class AP(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url='https://apnews.com/politics'
        self.selector =[]
    def get_archive_urls(self, url, selectors):
        """
        Implement get_archive_urls here to override behavior
        """
        return get_urls_ap(url)
    def crawl(self, startdate=[2018,10,13], enddate =[], delta_hrs=6):
        return super().crawl(startdate, enddate, delta_hrs)
    

    



       
