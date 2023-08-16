from newsfaces.utils import make_link_absolute
from .crawler import WaybackCrawler
import datetime
import pytz


class AP(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = ""
        self.selector = []

    def get_archive_urls(self, url, selectors):
        """
        This function takes a URLs and returns lists of URLs
        for containing each article on that page.

        Parameters:
            * url:  a URL to a page of articles
            * session: optional session object parameter
            * selectors: a list of css selectors

        Returns:
            A list of article URLs on that page.
        """
        response = self.make_request(url)
        urls = []
        selectors = [
            "div.FourColumnContainer-column",
            "div.TwoColumnContainer7030",
            "div.PageList-items",
            "article",
        ]
        for a in selectors:
            container = response.cssselect(a)
            if len(container) > 0:
                urls += self.parse_links(container)
        xpath_sel = ["TwoColumnContainer", "CardHeadline"]
        # for items that have random characters continually added at the end so we do non-exact matching
        for j in xpath_sel:
            container = response.xpath(f"//div[contains(@class, '{j}')]")
            if len(container) > 0:
                urls += self.parse_links(container)

        return urls

    def crawl(self):
        self.start_url = "https://apnews.com/politics"
        change_date = datetime.datetime(2023, 6, 26, 0, 0, tzinfo=pytz.timezone("utc"))
        if self.start_date < change_date:
            self.start_url = "https://apnews.com/hub/politics"
            self.end_date = change_date
            hub_site = super().crawl()
        self.start_url = self.urls[0]
        current_site = super().crawl()
        return hub_site.union(current_site)

    def parse_links(self, container):
        """
        Takes a list of container objects and returns the urls
        from within
        """
        urls = []
        for j in container[0]:
            atr = j.cssselect("a")
            for a in atr:
                href = a.get("href")
                if href is not None:
                    if href.startswith("/web/"):
                        href = make_link_absolute(href, "https://web.archive.org")
                    urls.append(href)
        return urls
    
        

