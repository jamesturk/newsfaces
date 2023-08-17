from ..crawler import WaybackCrawler
from ..utils import make_link_absolute
import lxml.html


class BreitbartArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("breitbart")
        self.start_url = "https://www.breitbart.com/politics/"
        self.selector = ["article"]

    def get_archive_urls(self, response):
        doc = lxml.html.fromstring(response.response_body)
        urls = []
        article_elements = doc.cssselect("article")
        for article in article_elements:
            atr = article.cssselect("a")
            if atr and len(atr) > 0:
                href = atr[0].get("href")
                if len(href) > 0:
                    urls.append(make_link_absolute(href, "https://web.archive.org/"))
        return urls
