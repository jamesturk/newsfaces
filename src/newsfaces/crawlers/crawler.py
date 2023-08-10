import time
import requests
import datetime
import lxml.html
import pytz
from wayback import WaybackClient, memento_url_data, WaybackSession
from ..utils import make_link_absolute
from ..models import ArticleURL

DEFAULT_DELAY = 0.5
START_DATE = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.timezone("utc"))
END_DATE = datetime.datetime.now(pytz.timezone("utc"))
DELTA_HRS = 6


class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.delay = DEFAULT_DELAY
        self.start_url = ""
        self.selectors = []
        self.prefix = None

    def http_get(self, url):
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
        response = self.http_get(url)
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
    def __init__(
        self,
        source_name: str,
        start_date: datetime.datetime = START_DATE,
        end_date: datetime.datetime = END_DATE,
        delta_hrs: int = DELTA_HRS,
    ):
        """
        start_date(datetime object): Earliest day for which to look for results
        end_date(datetime object): Latest day for which to look for results
        delta_hrs (int): Threshold of minimum number of hours between the
        timestamp of consecutive internet archive results for which to look for
        article urls.
        """
        super().__init__()
        self.session = WaybackSession()
        self.client = WaybackClient(self.session)
        self.source_name = source_name
        self.prefix = "https://web.archive.org/"
        self.start_date = start_date
        self.end_date = end_date
        self.delta_hrs = delta_hrs

    def get_wayback_urls(self):
        """
        Yield all wayback URLs between start_date and end_date
        """
        post_date_articles = set()

        # Get first result
        current_date = self.start_date
        results = self.client.search(
            self.start_url, match_type="exact", from_date=current_date
        )
        record = next(results)

        # Crawl internet archive in gaps of at least delta_hrs
        while current_date < self.end_date:
            yield ArticleURL(url=record.view_url, source=self.source_name)

            # If gap between fetched and next result is less than delta_hrs,
            # search the archive for the first results in at least delta_hrs
            try:
                next_result = next(results)
            except StopIteration:
                break
            next_time = next_result.timestamp
            if next_time - current_date < datetime.timedelta(hours=self.delta_hrs):
                current_date += datetime.timedelta(hours=self.delta_hrs)
                results = self.client.search(
                    self.start_url, match_type="exact", from_date=current_date
                )
                record = next(results)
            else:
                current_date = next_time
                record = next_result

    def crawl(self):
        """
        Crawl to obtain all the urls of articles contained in start_url in the different
        stored versions in the internet archive between two dates.
        """
        waybackurl = record.view_url
        articles = self.get_archive_urls(waybackurl, self.selector)
        articles = [
            memento_url_data(item)[0]
            if ("/web/" in item or "web.archive.org" in item)
            else item
            for item in articles
        ]
        post_date_articles.update(articles)
        return post_date_articles

    def get_archive_urls(self, url, selectors):
        """
        might be overriden in child class
        """
        articles = self.get_urls(url, selectors)

        return articles
