# Util Functions
import time
import requests
from urllib.parse import urlparse
import lxml.html
from wayback import WaybackClient, memento_url_data, WaybackSession
import itertools
import datetime
from utils import make_request, parse_html, make_link_absolute, page_grab
import pytz
from nbc import get_nbc
from politico import politico_get_urls
from ap import get_urls_ap

DEFAULT_DELAY = 0.5
url = ""
selectors = []

class Crawler(object):
    def __init__(self):  
        self.session = requests.Session()
        self.delay = DEFAULT_DELAY
        self.start_url = url
        self.selectors = selectors

    def make_request(self, url):
        """
        Make a request to `url` and return the raw response.

        This function ensure that the domain matches what is expected and that the rate limit
        is obeyed.
        """
        # check if URL starts with an allowed domain name
        time.sleep(self.delay)
        print(f"Fetching {url}")
        resp = self.session.get(url)
        return lxml.html.fromstring(resp.text)

    def crawl(self) -> list[str]:
        """
        Crawl the site and return a list of URLs to be scraped.
        """
        return self.get_urls(self.start_url, self.selectors)

    def get_urls(self, url, selectors):
        """
        This function takes a URLs and returns lists of URLs
        for containing each article on that page.

        Parameters:
            * url:  a URL to a page of articles
            * selectors: a list of css selectors

        Returns:
            A list of article URLs on that page.
        """
        response = self.make_request(url)
        urls = []
        for selector in selectors:
            container = response.cssselect(selector)
            for j in container:
                atr = j.cssselect("a")
                if atr and len(atr) > 0:
                    href = atr[0].get("href")
                    if len(href) > 0:
                        urls.append(
                            make_link_absolute(href, "https://web.archive.org/")
                        )
        return urls


class WaybackCrawler(Crawler):
    def __init__(self):  
        super().__init__()
        self.session = WaybackSession()
        self.client = WaybackClient(self.session)

    def crawl(self, startdate, enddate, delta_hrs):
        # Create datetime - objects to crawl using wayback
        year, month, day = startdate
        current_date = datetime.datetime(
            year, month, day, 0, 0, 0, tzinfo=pytz.timezone("utc")
        )
        year, month, day = enddate
        end_date = datetime.datetime(year, month, day, 0, 0, 0, tzinfo=pytz.timezone("utc"))
        post_date_articles = set()

        last_url_visited = None
        # Crawl internet archive once every delta_hrs from startdate until enddate
        while current_date < end_date:
            print(current_date, "next", end_date)
            results = self.client.search(
                self.start_url, match_type="exact", from_date=current_date
            )
            record = next(results)
            waybackurl = record.view_url
            # To avoid fetching urls multiple times, check if there are no updates in
            # the delta_hrs period
            if last_url_visited != waybackurl:
                articles = self.get_archive_urls(waybackurl, self.selector)
                print(articles)
                articles = [memento_url_data(item)[0] for item in articles]
                post_date_articles.update(articles)
                last_url_visited = waybackurl
            current_date += datetime.timedelta(hours=delta_hrs)
            next_time = next(results).timestamp
            if next_time > current_date:
                current_date = next_time
        return post_date_articles


    def get_archive_urls(self, url, selectors):
        """
        might be overriden in child class
        """
        return self.get_urls(url, selectors)

class s(Crawler):
    def crawl(self):
        """
        Implement crawl here to override behavior
        """


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



       
