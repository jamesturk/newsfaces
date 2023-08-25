from ..crawler import WaybackCrawler
from ..models import URL
import lxml.html
from ..extract_html import Extractor



class NBCArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("nbc")
        self.start_url = "https://www.nbcnews.com/politics"
        self.selector = []
        self.link_patterns = ["nbcnews.com/politics"]

    def get_article_urls(self, response):
        # Retrieve the raw HTML content
        html = response.text
        doc = lxml.html.fromstring(html)
        for link in doc.xpath("//a/@href"):
            for link_pattern in self.link_patterns:
                if link_pattern in link:
                    yield URL(url=link, source=self.source_name)

class NBC_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div.article-body__content"]
        self.img_p_selector = ["picture"]
        self.img_selector = ["img"]
        self.head_img_div = ['figure[class^="article-hero__main"]']
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1"]