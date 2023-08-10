from .crawler import WaybackCrawler


class TheHill(WaybackCrawler):
    def __init__(self):
        super().__init__("hill")
        self.start_url = "https://thehill.com/policy/"
        self.selector = ["div.archive__item__content", "h2.node__title.node-title"]
