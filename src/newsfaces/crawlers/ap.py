
from .crawler import WaybackCrawler
import datetime
import pytz
from newsfaces.extract_html import Extractor
from newsfaces.utils import make_link_absolute
import lxml.html


class APArchive(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.urls = ["https://apnews.com/politics", "https://apnews.com/hub/politics"]
        super().__init__("ap")
        self.start_url = ""
        self.selector = []

    def get_article_urls(self, response):
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
        doc = lxml.html.fromstring(response.text)
        selectors = [
            "div.FourColumnContainer-column",
            "div.TwoColumnContainer7030",
            "div.PageList-items",
            "article",
        ]
        for a in selectors:
            container = doc.cssselect(a)
            if len(container) > 0:
                yield from self.parse_links(container)
        xpath_sel = ["TwoColumnContainer", "CardHeadline"]
        # for items that have random characters continually added at the end so we do
        # non-exact matching
        for j in xpath_sel:
            container = response.xpath(f"//div[contains(@class, '{j}')]")
            if len(container) > 0:
                yield from self.parse_links(container)

    def crawl(self, startdate, enddate, delta_hrs=6):
        if startdate < datetime.datetime(
            2023, 6, 26, 0, 0, tzinfo=pytz.timezone("utc")
        ):
            self.start_url = self.urls[1]
            changepage_date = datetime.datetime(
                2023, 6, 26, 0, 0, tzinfo=pytz.timezone("utc")
            )
            hub_site = super().crawl(startdate, changepage_date, delta_hrs)
        self.start_url = self.urls[0]
        current_site = super().crawl(startdate, enddate, delta_hrs)
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



class AP_Extractor(Extractor):
    def __init__(self):
        super().__init__()

        self.article_body = ["main.Page-main"]
        self.img_p_selector = ["figure.Figure"]
        self.img_selector = ["img"]
        self.head_img_div = ["div.Page-lead"]
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1.Page-headline"]

    def get_wayback_urls(self):
        self.start_url = "https://apnews.com/hub/politics"
        yield from super().get_wayback_urls()
        # change_date = datetime.datetime(2023, 6, 26, 0, 0, tzinfo=pytz.timezone("utc"))
        # self.start_url = "https://apnews.com/politics"
        # yield from super().get_wayback_urls()

