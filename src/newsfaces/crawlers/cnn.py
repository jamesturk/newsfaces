from .crawler import WaybackCrawler


class CnnCrawler(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.cnn.com/politics/"
        self.selector = ["div.container__item", "h3.cd__headline"]
