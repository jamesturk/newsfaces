from crawler import Crawler,WaybackCrawler
import time
import re
from utils import make_link_absolute
from wayback import WaybackClient, memento_url_data, WaybackSession

class NprCrawler(Crawler):

    def __init__(self):
        super().__init__()
        self.url = "https://www.npr.org/sections/politics/archive?"
    
    def obtain_page_urls(self, start="0",date="12-31-2023"):
        """
        Obtain the URLS of a page from the politics section using the NPR internal API
        Inputs:
        start(str/int): Article to start seach from (Similar to page)
        date(str): Date to start looking articles from sorted from newest to oldest
        Return:
        url_set(set): Set of articles
        month(int): Month of last article retrieved

        """
        url = self.url + "start={}&date={}".format(start,date)
        root = self.make_request(url)
        article_elements = root.cssselect("h2.title")
        if len(article_elements) == 0:
            return None
        links_list = []
        for element in article_elements:
            link = element.cssselect("a")
            href = link[0].get("href")
            links_list.append(href)
        month = re.search(r"(?<=\d{4}/)\d{2}",links_list[-1]).group()

        url_set = set(links_list)

        return url_set, int(month)

    def obtain_monthly_urls(self,start=0,month=12,year=2023):
        """ 
        Obtain the urls from the NPR politics section for a given month
        Inputs:
        - start(int): Article to start seach from (Similar to page)
        - month(int): Month to obtain articles from
        - year(int): Year to obtain articles from

        Return:
        month_urls (set): Set of articles of the politics section the month specified
        """
        
        last_day_month ={1:31,2:28,3:31,4:30,5:31,6:30,7:31,8:31,9:30,10:31,11:30,12:31}

        date = "{}-{}-{}".format(month,last_day_month[month],year)
        month_urls = set()
        page = 1
        print("Obtaining links for ",month,"-",year, ",page:",page)
        current_month = month
        while  current_month == month:
            page_urls, current_month = self.obtain_page_urls(start,date)
            month_urls.update(page_urls)
            start += 15
            page += 1
            print("Obtaining links for ",month,"-",year, ",page:",page)
        
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
        for year in range(min_year,2024):
            for month in range(1,13):
                articles_set.update(self.obtain_monthly_urls(0,month,year))

        return articles_set
    

class NewsmaxCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://www.newsmax.com/archives/politics/1/"

    def obtain_page_urls(self,year="2016",month="1"):
        """
        Obtain the urls for a given year and month from the politics section of Newsmax
        Inputs:
        -year(str): Year of the articles to search for
        -month(str): Month of the articles to search for
        Return:
        links_list(list): List of urls 
        """
        url = self.url + "{}/{}/".format(year,month)
        root = self.make_request(url)
        links_elements = root.cssselect("h5.archiveH5")
        links_list = []
        for element in links_elements:
            link = element.cssselect("a")
            href = link[0].get("href")
            full_link = "newsmax.com" + href
            links_list.append(full_link)
        return links_list
    
    def crawl(self,min_year=2016):
        """
        Obtain all newsmax urls from the politics section
        Inputs: None
        Return:
        newsmax_links (dict): Dictionary where the keys are str for date (year-mth)
        and values are lists with the urls of that given key
        """
        years = [*range(min_year,2024,1)]
        months = [*range(1,13,1)]
        articles_set = set()        

        #Obtain news for 
        for year in years:
            for month in months:
                date = str(year) + "-" + str(month)
                print("Obtaining news from:",date)
                articles_set.update(self.obtain_page_urls(str(year),str(month)))

        return articles_set 


class DailyCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://dailycaller.com/section/politics/"

    def obtain_page_urls(self,page="1"):
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
            #Some articles in the Daily Caller politcs section
            #Are articles from another webpage checkyourfact and we will drop these
            if link.startswith("http://checkyourfact"):
                continue
            full_link = "dailycaller.com" + link

            article_list.append(full_link)
        
        year = re.search(r'\d{4}',article_list[-1]).group()
        print("Year:",year)
        articles_set = set(article_list)

        return articles_set, int(year)
    
    def obtain_year_urls(self,page = 1,year=2023):
        """ 
        Obtain the results of 
        """
        links_set  = set ()
        article_year = 2023
        while article_year >= year: 
            print("Obtaining results for page", page)
            page_links, article_year = self.obtain_page_urls(str(page))
            links_set.update(page_links)
            page += 1
        
        return links_set, page
    
    def crawl(self,min_year = 2016):
        """
        Starting from 2023 it fetches the urls of the daily caller politics section
        """
        years = [*range(min_year,2024,1)]
        page = 1
        articles_set = set()
        for year in reversed(years):
            print("Obtainings links for", year)
            year_set, page = self.obtain_year_urls(page,year)
            articles_set.update(year_set)
            page += 1

        return articles_set()
    
    def crawl_non_wayback(self, min_year=2016):
        cnn_links = set()
        #Crawl and retrieve Urls using helper function
        from_art = 0
        page = 1
        year = 9999
        
        page_set_len = 0

        while int(year) >= min_year:
            print("Obtaining results for page", page)
            page_urls, year = self.obtain_page_urls(from_art,page)
            cnn_links.update(page_urls)
            from_art += 10
            page += 1
            len_set = (len(cnn_links))
            if len_set == page_set_len:
                break
            else:
                page_set_len = len_set

        return cnn_links

class BreitbartCrawler(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url="https://www.breitbart.com/politics/"
        self.session = WaybackSession()
        self.client = WaybackClient(self.session)
        self.selector = None

    def get_archive_urls(self, url, selector = [""]):
        response = self.make_request(url)
        urls = []
        article_elements = response.cssselect("article")
        for article in article_elements:
                atr = article.cssselect("a")
                if atr and len(atr) > 0:
                    href = atr[0].get("href")
                    if len(href) > 0:
                        urls.append(
                            make_link_absolute(href, "https://web.archive.org/")
                        )
        return urls


class CnnCrawler(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url="https://www.cnn.com/politics/"
        self.selector = ["div.container__item",
        "h3.cd__headline"]
