from ..crawler import WaybackCrawler
from ..models import URL
import lxml.html


class NBCArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("nbc")
        self.start_url = "https://www.nbcnews.com/politics"
        self.selector = []
        self.link_patterns = ["nbcnews.com/politics"]

    def get_article_urls(self, response):
        # Retrieve the raw HTML content
        html = response.response_body
        doc = lxml.html.fromstring(html)
        for link in doc.xpath("//a/@href"):
            for link_pattern in self.link_patterns:
                if link_pattern in link:
                    yield URL(url=link, source=self.source_name)

