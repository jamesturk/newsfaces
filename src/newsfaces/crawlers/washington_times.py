from ..crawler import WaybackCrawler
from ..extract_html import Extractor


class WashingtonTimesArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("washtimes")
        self.start_url = "https://www.washingtontimes.com/news/politics/"
        self.selector = ["article"]


class WashingtonTimes_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div.storyareawrapper", "article"]
        self.img_p_selector = ["div.photo"]
        self.img_selector = ["img"]
        self.head_img_div = ["figure.photo-zoom"]
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1.page-headline"]
