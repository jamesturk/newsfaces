import re
from crawler import Crawler


class DailyCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://dailycaller.com/section/politics/"

    def obtain_page_urls(self, page="1"):
        """
        Obtain the urls of the politics section of a url in the Daily Caller politics
        section
        Inputs:
        - page(str): page of the politics section to fetch urls
        Return:
        - articles_set (set): Set of unique urls
        - year (int): year of last article fetched on the page
        """
        url = self.url + "page/{}/".format(page)
        root = self.make_request(url)
        article_elements = root.cssselect("article.relative")
        article_list = []
        for article in article_elements:
            link = article.cssselect("a")[0].get("href")
            # Some articles in the Daily Caller politcs section
            # Are articles from another webpage checkyourfact and we will drop these
            if link.startswith("http://checkyourfact"):
                continue
            full_link = "dailycaller.com" + link

            article_list.append(full_link)

        year = re.search(r"\d{4}", article_list[-1]).group()
        print("Year:", year)
        articles_set = set(article_list)

        return articles_set, int(year)

    def obtain_year_urls(self, page=1, year=2023):
        """
        Obtain the results of
        """
        links_set = set()
        article_year = 2023
        while article_year >= year:
            print("Obtaining results for page", page)
            page_links, article_year = self.obtain_page_urls(str(page))
            links_set.update(page_links)
            page += 1

        return links_set, page

    def crawl(self, min_year=2016):
        """
        Starting from 2023 it fetches the urls of the daily caller politics section
        """
        years = [*range(min_year, 2024, 1)]
        page = 1
        articles_set = set()
        for year in reversed(years):
            print("Obtainings links for", year)
            year_set, page = self.obtain_year_urls(page, year)
            articles_set.update(year_set)
            page += 1

        return articles_set()

    def crawl_non_wayback(self, min_year=2016):
        cnn_links = set()
        # Crawl and retrieve Urls using helper function
        from_art = 0
        page = 1
        year = 9999

        page_set_len = 0

        while int(year) >= min_year:
            print("Obtaining results for page", page)
            page_urls, year = self.obtain_page_urls(from_art, page)
            cnn_links.update(page_urls)
            from_art += 10
            page += 1
            len_set = len(cnn_links)
            if len_set == page_set_len:
                break
            else:
                page_set_len = len_set

        return cnn_links
