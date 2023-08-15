from ..crawler import WaybackCrawler, WaybackClient, WaybackSession
from newsfaces.utils import make_link_absolute


class BreitbartCrawler(WaybackCrawler):
    def __init__(self):
        super().__init__("breitbart")
        self.start_url = "https://www.breitbart.com/politics/"
        self.selector = ["article"]

    # def get_archive_urls(self, response):
    #     response = self.make_request(url)
    #     doc = lxml.html.fromstring(response.content)
    #     urls = []
    #     article_elements = doc.cssselect("article")
    #     for article in article_elements:
    #         atr = article.cssselect("a")
    #         if atr and len(atr) > 0:
    #             href = atr[0].get("href")
    #             if len(href) > 0:
    #                 urls.append(make_link_absolute(href, "https://web.archive.org/"))
    #     return urls
