from ..models import URL
from ..extract_html import Extractor
from ..utils import make_link_absolute
from ..crawler import Crawler, WaybackCrawler
import json


class FoxArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("fox")
        self.start_url = "https://www.foxnews.com/politics"
        self.selector = ["article"]


class Fox_API(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url = (
            "https://www.foxnews.com/api/article-search?searchBy=categories"
            "&values=fox-news%2Fpolitics&size=30&from=15&mediaTags=primary_politics"
        )
        self.source = "fox_api"

    def crawl(self):
        """
        run get_html with correct initial html from init
        """
        url = self.start_url
        articlenumber = 0
        while articlenumber < 9970:
            yield from self.get_newslinks(url)
            begin = url.find("from") + 5
            end = url.find("&media")
            articlenumber = int(url[begin:end])
            articlenumber += 30
            url = url[:begin] + str(articlenumber) + url[end:]

    def get_newslinks(self, base_page):
        """
        From an initial API query page, run through all possible
        API queries-- putting articles and videos on the pages into
        a set.

        Returns:
        Set of articles and videos
        """
        response = self.http_get(base_page)
        json_data = json.loads(response.text)
        for i in json_data:
            url = make_link_absolute(i["url"], "https://www.foxnews.com/politics")
            if url.startswith("https://www.foxnews.com/politics"):
                yield URL(url=url, source=self.source)
            else:
                pass  # TODO: video


class Fox_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div.article-content-wrap.sticky-columns", "article"]
        self.img_p_selector = ["div[class^=image]"]
        self.img_selector = ["img"]
        self.head_img_div = None
        self.head_img_select = None
        self.p_selector = ["p"]
        self.t_selector = ["h1.headline", "h1"]
    def get_img_caption(self, img):
        caption_div = img.xpath(".//following::div[contains(@class, 'caption')][1]")
        if caption_div:
            caption_text = caption_div[0].text_content().strip()
            return caption_text
        else:
            return ""