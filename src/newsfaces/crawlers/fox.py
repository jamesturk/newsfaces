# Util Functions
from newsfaces.utils import make_link_absolute
from .crawler import Crawler, WaybackCrawler
import json


class Fox(WaybackCrawler):
    def __init__(self):
        super().__init__("fox")
        self.start_url = "https://www.foxnews.com/politics"
        self.selector = ["article"]


class Fox_API(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.foxnews.com/api/article-search?searchBy=categories&values=fox-news%2Fpolitics&size=30&from=15&mediaTags=primary_politics"

    def crawl(self):
        """
        run get_html with correct initial html from init
        """
        return self.get_newslinks(self.start_url)

    def get_newslinks(self, base_page, article=set(), video=set()):
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
                article.add(url)
            else:
                video.add(url)
        begin = base_page.find("from") + 5
        end = base_page.find("&media")
        articlenumber = int(base_page[begin:end])
        if articlenumber < 9970:
            articlenumber += 30
            articlenumber = str(articlenumber)
            rev_basepage = (
                base_page[0:begin]
                + articlenumber
                + base_page[end : (len(base_page) + 1)]
            )
            self.get_newslinks(rev_basepage, article, video)
        return article.union(video)
