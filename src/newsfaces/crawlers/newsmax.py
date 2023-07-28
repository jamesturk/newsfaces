from .crawler import Crawler
import datetime

CURRENT_YEAR = datetime.datetime.now().year

class NewsmaxCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.newsmax.com/archives/politics/1/"

    def obtain_page_urls(self, year="2016", month="1"):
        """
        Obtain the urls for a given year and month from the politics section of Newsmax
        Inputs:
        -year(str): Year of the articles to search for
        -month(str): Month of the articles to search for
        Return:
        links_list(list): List of urls
        """
        url = self.url + "{}/{}/".format(year, month)
        root = self.make_request(url)
        links_elements = root.cssselect("h5.archiveH5")
        links_list = []
        for element in links_elements:
            link = element.cssselect("a")
            href = link[0].get("href")
            full_link = "newsmax.com" + href
            links_list.append(full_link)
        return links_list

    def crawl(self, min_year=2015):
        """
        Obtain all newsmax urls from the politics section
        Inputs: None
        Return:
        newsmax_links (dict): Dictionary where the keys are str for date (year-mth)
        and values are lists with the urls of that given key
        """

        articles_set = set()

        # Obtain news for
        for year in range(min_year,CURRENT_YEAR+1):
            for month in range(1,13):
                date = str(year) + "-" + str(month)
                print("Obtaining news from:", date)
                articles_set.update(self.obtain_page_urls(str(year), str(month)))

        return articles_set
