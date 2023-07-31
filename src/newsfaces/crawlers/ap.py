
from newsfaces.utils import make_link_absolute
from .crawler import WaybackCrawler


class AP(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://apnews.com/politics"
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
                for j in container[0]:
                    atr = j.cssselect("a")
                    for a in atr:
                        href = a.get("href")
                        if href is not None:
                            if href.startswith("/web/"):
                                href = make_link_absolute(href, "https://web.archive.org")
                            urls.append(href)
        return urls

    def crawl(self, startdate=[2018, 10, 13], enddate=[], delta_hrs=6):
        return super().crawl(startdate, enddate, delta_hrs)
