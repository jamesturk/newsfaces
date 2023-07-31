# Util Functions
import time
import requests
import lxml.html
from wayback import WaybackClient, memento_url_data, WaybackSession
import datetime
from newsfaces.utils import make_link_absolute
import pytz

DEFAULT_DELAY = 0.5


class Crawler(object):
    def __init__(self):
        self.session = requests.Session()
        self.delay = DEFAULT_DELAY
        self.start_url = ""
        self.selectors = []
        self.prefix = None

    def html_grab(self, url):
        """
        Make a request to `url` and return the raw response.

        This function ensure that the domain matches what is
        expected and that the rate limit is obeyed.
        """
        time.sleep(self.delay)
        print(f"Fetching {url}")
        resp = self.session.get(url)
        return resp    

    def make_request(self, url):
        """
        Make a request to `url` and returns usable HTML via lxml.
        """
        # check if URL starts with an allowed domain name
        response = self.html_grab(url)
        return lxml.html.fromstring(response.text)


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
                        if self.prefix is not None:
                            urls.append(make_link_absolute(href, self.prefix))
                        else:
                            urls.append(href)
        return urls


class WaybackCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.session = WaybackSession()
        self.client = WaybackClient(self.session)
        self.prefix = "https://web.archive.org/"

    def crawl(self, startdate, enddate, delta_hrs=6):
        post_date_articles = set()

        # Create datetime - objects to crawl using wayback
        year, month, day = startdate
        current_date = datetime.datetime(
            year, month, day, 0, 0, 0, tzinfo=pytz.timezone("utc")
        )

        year, month, day = enddate
        end_date = datetime.datetime(
            year, month, day, 0, 0, 0, tzinfo=pytz.timezone("utc")
        )

        # Get first result
        results = self.client.search(
            self.start_url, match_type="exact", from_date=current_date
        )
        record = next(results)

        # Crawl internet archive in gaps of at least delta_hrs
        while current_date < end_date:
            # Get URL
            waybackurl = record.view_url
            articles = self.get_archive_urls(waybackurl, self.selector)
            articles = [
                memento_url_data(item)[0]
                if (item.find("/web/") or item.find("web.archive.org") in item)
                else item
                for item in articles
            ]
            post_date_articles.update(articles)
            # If gap between fetched and next result is less than delta_hrs,
            # search the archive for the first results in at least delta_hrs
            next_time = next(results).timestamp
            if next_time - current_date < datetime.timedelta(hours=delta_hrs):
                current_date += datetime.timedelta(hours=delta_hrs)
                results = self.client.search(
                    self.start_url, match_type="exact", from_date=current_date
                )
                record = next(results)
            else:
                current_date = next_time
        return post_date_articles

    def get_archive_urls(self, url, selectors):
        """
        might be overriden in child class
        """
        articles = self.get_urls(url, selectors)

        return articles
