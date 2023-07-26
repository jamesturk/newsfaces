class WashingtonTimes(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.washingtontimes.com/news/politics/"
        self.selector = ["article"]
