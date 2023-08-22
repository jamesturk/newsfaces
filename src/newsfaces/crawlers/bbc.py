from ..crawler import Crawler, WaybackCrawler
from newsfaces.utils import make_link_absolute
from newsfaces.models import URL


class BBC_Latest(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.bbc.com/news/topics/cwnpxwzd269t?page=1"
        self.source = "bbc_latest"

    def crawl(self):
        """
        run get_html with correct initial html from init
        """
        url = self.start_url
        pagenumber = 0
        while pagenumber < 42:
            yield from self.get_urls(url)
            pagenumber += 1
            # TODO: why 42?
            if pagenumber < 42:
                url = url[: -len(str(pagenumber))] + str(pagenumber + 1)

    def get_urls(self, url):
        """
        This function takes a URLs and returns lists of URLs
        for containing each article and video on that page.

        Parameters:
            * url:  a URL to a page of articles

        Returns:
            A list of URLs to each video and article on that page.
        """
        response = self.make_request(url)
        container = response.cssselect("div")
        filtered_container = [
            elem for elem in container if elem.get("type") is not None
        ]

        for j in filtered_container:
            # find video/article
            type = j.get("type")
            # find link
            if type == "article" or type == "video":
                a = j[0].cssselect("a")
                href = a[0].get("href")
                href = make_link_absolute(href, "https://www.bbc.com")
            if type == "article":
                yield URL(url=href, source=self.source)
            elif type == "video":
                pass  # TODO: video


class BBCArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("bbc")
        self.start_url = "https://www.bbc.com/news/topics/cwnpxwzd269t"
        self.selector = ["article"]
