from crawler import Crawler, WaybackCrawler
import time
import re
from utils import make_link_absolute
from wayback import WaybackClient, memento_url_data, WaybackSession


class CnnCrawler(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.cnn.com/politics/"
        self.selector = ["div.container__item", "h3.cd__headline"]
