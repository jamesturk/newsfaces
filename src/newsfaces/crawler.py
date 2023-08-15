import time
import requests
import datetime
import lxml.html
import pytz
from typing import Generator
from wayback import WaybackClient, memento_url_data, WaybackSession
from .utils import make_link_absolute
from .models import ArticleURL
from databeakers.http import HttpResponse

DEFAULT_DELAY = 0.5
START_DATE = datetime.datetime(2020, 1, 1, 0, 0, tzinfo=pytz.timezone("utc"))
END_DATE = datetime.datetime.now(pytz.timezone("utc"))
DELTA_HRS = 6


class Crawler:
    def __init__(self):
        self.session = requests.Session()
        self.delay = DEFAULT_DELAY
        self.start_url = ""
        self.selector = []
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
        return self.get_urls(self.start_url, self.selector)

    def get_article_urls(
        self, response: HttpResponse
    ) -> Generator[ArticleURL, None, None]:
        """
        This function takes a response & a list of css selectors and returns
        a list of URLs.

        Parameters:
            * response: a response object
            * selectors: a list of css selectors

        Returns:
            A list of article URLs on that page.
        """
        doc = lxml.html.fromstring(response.response_body)
        urls = []
        for selector in self.selector:
            container = doc.cssselect(selector)
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
        current_date = self.start_date

        # get first result
        # each search result will contain multiple URLs
        results = self.client.search(
            self.start_url, match_type="exact", from_date=current_date
        )

        while current_date < self.end_date:
            # get a new record and yield the URL
            try:
                record = next(results)
            except StopIteration:
                break

            next_time = record.timestamp

            # if the next result is too close, skip it
            if next_time - current_date < datetime.timedelta(hours=self.delta_hrs):
                current_date += datetime.timedelta(hours=self.delta_hrs)
                results = self.client.search(
                    self.start_url, match_type="exact", from_date=current_date
                )
                continue

            # yield back the article URL and update the date cursor
            yield ArticleURL(url=record.view_url, source=self.source_name)
            current_date = next_time

    def get_article_urls(
        self, response: HttpResponse
    ) -> Generator[ArticleURL, None, None]:
        """
        Get all article URLs from a wayback URL
        """
        articles = super().get_article_urls(response)
        # convert to normal URLs
        for item in articles:
            if "/web/" in item or "web.archive.org" in item:
                yield ArticleURL(url=memento_url_data(item)[0], source=self.source_name)
            else:
                yield ArticleURL(url=item, source=self.source_name)
