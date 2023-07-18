# Util Functions
import time
import requests
from urllib.parse import urlparse
import lxml.html
from wayback import WaybackClient, memento_url_data, WaybackSession
import itertools
import datetime
from utils import make_request, parse_html, make_link_absolute, page_grab 

DEFAULT_DELAY = 0.5



class Crawler:
    """
    Need to define at least two properties:
    * start_url: the URL to start crawling from
    * selectors: a list of css selectors
    """

    def __init__(self):
        self.session = requests.Session()
        self.delay = DEFAULT_DELAY
        self.url=""
        self.selector=[]

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
        self.session = WaybackSession()
        self.client = WaybackClient(self.session)

    # def crawl(self, startdate, break_point):
    #     results = self.client.search(self.url, match_type="exact", from_date=startdate)
    #     crosstime_urls = list(itertools.islice(results, break_point))
    #     post_date_articles = set()
    #     for i in range(len(crosstime_urls)):
    #         date = datetime.datetime.strptime(startdate, "%Y%m%d")
    #         if crosstime_urls[i].timestamp.date() >= date.date():
    #             articles = self.get_archive_urls(crosstime_urls[i].view_url, Crawler.selectors)
    #             # converts archive links back to current article links
    #             articles = [memento_url_data(item)[0] for item in articles]
    #             post_date_articles.update(articles)
    #     return post_date_articles

    def crawl(self,startdate,enddate,delta_hrs):
        #Create datetime - objects to crawl using wayback
        year, month, day = startdate
        current_date = datetime.datetime(year,month,day)
        year, month, day = enddate
        end_date = datetime.datetime(year,month,day)
        post_date_articles = set()

        last_url_visited = None

        #Crawl internet archive once every delta_hrs from startdate until enddate
        while current_date != end_date:
            results = self.client.search(self.url, match_type="exact", from_date=current_date)
            record = next(results)
            url = record.view_url
            #To avoid fetching urls multiple times, check if there are no updates in
            #the delta_hrs period
            if last_url_visited != url:
                articles = self.get_archive_urls(url,self.selector,self.session)
                articles = [memento_url_data(item)[0] for item in articles]
                post_date_articles.update(articles)

            last_url_visited = url
            current_date += datetime.timedelta(hours = delta_hrs)
        return post_date_articles
    
    def get_archive_urls(self, url, selectors):
        """
        might be overriden in child class
        """
        return self.get_urls(url, selectors)


class DailyCaller(Crawler):
    def crawl(self):
        """
        Implement crawl here to override behavior
        """


class WashingtonPost(WaybackCrawler):
    def get_archive_urls(self, url, selectors):
        """
        Implement get_archive_urls here to override behavior
        """
