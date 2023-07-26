from .crawler import Crawler
import re


class NprCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.npr.org/sections/politics/archive?"

    def obtain_page_urls(self, start="0", date="12-31-2023"):
        """
        Obtain the URLS of a page from the politics section using the NPR internal API
        Inputs:
        start(str/int): Article to start seach from (Similar to page)
        date(str): Date to start looking articles from sorted from newest to oldest
        Return:
        url_set(set): Set of articles
        month(int): Month of last article retrieved

        """
        url = self.url + "start={}&date={}".format(start, date)
        root = self.make_request(url)
        article_elements = root.cssselect("h2.title")
        if len(article_elements) == 0:
            return None
        links_list = []
        for element in article_elements:
            link = element.cssselect("a")
            href = link[0].get("href")
            links_list.append(href)
        month = re.search(r"(?<=\d{4}/)\d{2}", links_list[-1]).group()

        url_set = set(links_list)

        return url_set, int(month)

    def obtain_monthly_urls(self, start=0, month=12, year=2023):
        """
        Obtain the urls from the NPR politics section for a given month
        Inputs:
        - start(int): Article to start seach from (Similar to page)
        - month(int): Month to obtain articles from
        - year(int): Year to obtain articles from

        Return:
        month_urls (set): Set of articles of the politics section the month specified
        """

        last_day_month = {
            1: 31,
            2: 28,
            3: 31,
            4: 30,
            5: 31,
            6: 30,
            7: 31,
            8: 31,
            9: 30,
            10: 31,
            11: 30,
            12: 31,
        }

        date = "{}-{}-{}".format(month, last_day_month[month], year)
        month_urls = set()
        page = 1
        print("Obtaining links for ", month, "-", year, ",page:", page)
        current_month = month
        while current_month == month:
            page_urls, current_month = self.obtain_page_urls(start, date)
            month_urls.update(page_urls)
            start += 15
            page += 1
            print("Obtaining links for ", month, "-", year, ",page:", page)

        return month_urls

    def crawl(self, min_year):
        """
        Crawl the NPR politics section
        Inputs:
        - min_year(int): Oldest year to get results from
        Return:
        - npr_url(set): Set of all the NPR politics section url until the specified year
        """
        articles_set = set()
        for year in range(min_year, 2024):
            for month in range(1, 13):
                articles_set.update(self.obtain_monthly_urls(0, month, year))

        return articles_set
