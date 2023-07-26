class BreitbartCrawler(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.breitbart.com/politics/"
        self.session = WaybackSession()
        self.client = WaybackClient(self.session)
        self.selector = None

    def get_archive_urls(self, url, selector=[""]):
        response = self.make_request(url)
        urls = []
        article_elements = response.cssselect("article")
        for article in article_elements:
            atr = article.cssselect("a")
            if atr and len(atr) > 0:
                href = atr[0].get("href")
                if len(href) > 0:
                    urls.append(make_link_absolute(href, "https://web.archive.org/"))
        return urls
