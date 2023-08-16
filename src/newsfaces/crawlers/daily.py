import re
import datetime
from newsfaces.models import URL
from ..crawler import Crawler
from ..utils import make_link_absolute


class DailyCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://dailycaller.com/section/politics/"
        self.prefix = "https://dailycaller.com/"
        self.source = "daily"

    def obtain_page_urls(self, page="1"):
        """
        Obtain the urls of the politics section of a url in the Daily Caller politics
        section

        Inputs:
            - page(str): page of the politics section to fetch urls
        Yields:
            - url(URl): url of the article
            - year(str): year of the article
        """
        url = self.url + "page/{}/".format(page)
        root = self.make_request(url)
        article_elements = root.cssselect("article.relative")
        for article in article_elements:
            link = article.cssselect("a")[0].get("href")
            # Some articles in the Daily Caller politcs section
            # Are articles from another webpage checkyourfact and we will drop these
            if link.startswith("http://checkyourfact"):
                continue
            full_link = make_link_absolute(link, self.prefix)
            year = re.search(r"\d{4}", full_link).group()
            yield URL(url=full_link, source=self.source), int(year)

    def crawl(self, start_date=datetime.date(2015, 1, 1)):
        """
        Starting from 2023 it fetches the urls of the daily caller politics section
        """
        min_year = int(start_date.strftime("%Y"))
        years = [*range(min_year, 2024, 1)]
        page = 1
        for year in reversed(years):
            print("Obtaining links for", year)
            article_year = 2023
            while article_year >= year:
                print("Obtaining results for page", page)
                for url, year in self.obtain_page_urls(str(page)):
                    yield url
                page += 1
