from ..crawler import WaybackCrawler
from ..extract_html import Extractor


class TheHillArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("hill")
        self.start_url = "https://thehill.com/policy/"
        self.selector = ["div.archive__item__content", "h2.node__title.node-title"]

class Hill_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div.article__text"]
        self.img_p_selector = ['figure[class^="wp-block-image"]']
        self.img_selector = ["img"]
        self.head_img_div = ["figure.article__featured-image"]
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1"]