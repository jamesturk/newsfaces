import json
from ..crawler import Crawler, WaybackCrawler
from newsfaces.utils import make_link_absolute
from newsfaces.models import URL


class WashingtonPost_API(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url = (
            "https://www.washingtonpost.com/prism/api/prism-query?_website=washpost"
            "&query=%7B%22query%22%3A%22prism%3A%2F%2Fprism.query%2Fsite-articles-only"
            "%2C%2Fpolitics%26offset%3D600%26limit%3D30%22%7D"
        )
        self.source = "wapo_api"

    def crawl(self):
        """
        run get_html with correct initial html from init
        """
        url = self.start_url
        articlenumber = 0
        while articlenumber < 9960:
            yield from self.get_html(url)

            begin = url.find("offset") + 9
            end = url.find("%26limit")
            try:
                articlenumber = int(url[begin:end])
            except ValueError:
                break
            articlenumber += 30
            url = url[:begin] + str(articlenumber) + url[end:]

    def get_html(self, base_page):
        """
        From an initial API query page, run through all possible
        API queries-- putting articles on the pages into
        a set.

        Returns:
        Set of articles
        """
        response = self.http_get(base_page)
        json_data = json.loads(response.text)
        for i in range(len(json_data)):
            url_text = json_data["items"][i]["canonical_url"]
            url = make_link_absolute(
                url_text, "https://www.washingtonpost.com/politics"
            )
            if url.startswith("https://www.washingtonpost.com/politics"):
                yield URL(url=url, source=self.source)
            else:
                pass  # TODO: video


class WashingtonPostArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("wapo")
        self.start_url = "https://www.washingtonpost.com/politics/"
        self.selector = ["div.story-headline"]

    def get_article_urls(self, response):
        for url in super().get_article_urls(response):
            if "https://www.washingtonpost.com/politics/2" in url.url:
                yield url
