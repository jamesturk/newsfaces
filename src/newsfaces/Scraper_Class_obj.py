# Util Functions
from crawlers.utils import make_request, make_link_absolute, page_grab
from nbc import get_nbc
from politico import politico_get_urls
from ap import get_urls_ap
from crawlers.crawler import Crawler, WaybackCrawler
import json


class Fox(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.foxnews.com/politics"
        self.selector = ["article"]

class Fox_API(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url="https://www.foxnews.com/api/article-search?searchBy=categories&values=fox-news%2Fpolitics&size=30&from=15&mediaTags=primary_politics"

    def crawl(self, base_page, article=set(), video=set()):
        """
        From an initial API query page, run through all possible
        API queries-- putting articles and videos on the pages into
        a set.

        Returns:
        Set of articles and videos
        """
        response = page_grab(base_page)
        json_data = json.loads(response.text)
        json_data
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
                base_page[0:begin] + articlenumber + base_page[end : (len(base_page) + 1)]
            )
            self.crawl(rev_basepage, article, video)
        return article.union(video)


class WashingtonTimes(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = 'https://www.washingtontimes.com/news/politics/'
        self.selector = ["article"]

class NBC(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url='https://www.nbcnews.com/politics/'
        self.selector =[]
    def get_archive_urls(self, url, selectors):
        """
        Implement get_archive_urls here to override behavior
        """
        return get_nbc(url, self.session)

class Politico(Crawler):
    def __init__(self):
        super().__init__()

    def crawl(self):
        """
        Implement crawl here to override behavior
        """
        return politico_get_urls()

class TheHill(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = 'https://thehill.com/policy/'
        self.selector = ['div.archive__item__content','h2.node__title.node-title']

class AP(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url='https://apnews.com/politics'
        self.selector =[]
    def get_archive_urls(self, url, selectors):
        """
        Implement get_archive_urls here to override behavior
        """
        return get_urls_ap(url)
    def crawl(self, startdate=[2018,10,13], enddate =[], delta_hrs=6):
        return super().crawl(startdate, enddate, delta_hrs)
        

    
class BBC_Latest(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url="https://www.bbc.com/news/topics/cwnpxwzd269t?page=1"

    def crawl(self, url=None, articles=set(), videos=set()):
        '''
        Takes an initial url and runs get_urls on all possible
        API queries. Gathering all possible articles and videos
        from the API into a set. 
        '''
        if url is None:
            url = self.start_url
        article, video = self.get_urls(url)
        articles = articles.union(article)
        videos = videos.union(video)
        begin = url.find("page=") + 5
        pagenumber = int(url[begin : len(url)])
        if pagenumber < 42:
            newlink = url[: -len(str(pagenumber))] + str(pagenumber + 1)
            article, video = self.crawl(newlink, articles, videos)
            articles = articles.union(article)
            videos = videos.union(video)
        return articles, videos
    
    def get_urls(self, url, articles=set(), videos=set()):
        """
        This function takes a URLs and returns lists of URLs
        for containing each article and video on that page.

        Parameters:
            * url:  a URL to a page of articles

        Returns:
            A list of URLs to each video and article on that page.
        """
        response = page_grab(url)
        urls = []
        container = response.cssselect('div')
        filtered_container = [elem for elem in container if elem.get("type") is not None]

        for j in filtered_container:
            # find video/article
            type = j.get("type")
            # find link
            if type == "article" or type == "video":
                a = j[0].cssselect("a")
                href = a[0].get("href")
                href = make_link_absolute(href, "https://www.bbc.com")
            if type == "article":
                articles.add(href)
            elif type == "video":
                videos.add(href)
        return articles, videos

class BBC(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = 'https://www.bbc.com/news/topics/cwnpxwzd269t'
        self.selector = ['div.archive__item__content','h2.node__title.node-title']
    def get_archive_urls(self, url, selector):
        return self.get(url)
    def get(self, url, articles=set(), videos=set()):
        """
        This function takes a URLs and returns lists of URLs
        for containing each article and video on that page.

        Parameters:
            * url:  a URL to a page of articles

        Returns:
            A list of URLs to each video and article on that page.
        """
        response = page_grab(url)
        urls = []
        container = response.cssselect('div')
        filtered_container = [elem for elem in container if elem.get("type") is not None]

        for j in filtered_container:
            # find video/article
            type = j.get("type")
            # find link
            if type == "article" or type == "video":
                a = j[0].cssselect("a")
                href = a[0].get("href")
                href = make_link_absolute(href, " https://web.archive.org")
            if type == "article":
                articles.add(href)
            elif type == "video":
                videos.add(href)
        print(articles)
        return articles.union(videos)
    
class WashingtonPost_API(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url='https://www.washingtonpost.com/prism/api/prism-query?_website=washpost&query=%7B%22query%22%3A%22prism%3A%2F%2Fprism.query%2Fsite-articles-only%2C%2Fpolitics%26offset%3D600%26limit%3D30%22%7D'

    def crawl(self, base_page, article=set(), video=set()):

        """
        From an initial API query page, run through all possible
        API queries-- putting articles on the pages into
        a set.

        Returns:
        Set of articles 
        """
        response = make_request(base_page)
        json_data = json.loads(response.text)
        for i in range(len(json_data)):
            url_text=json_data["items"][i]['canonical_url']
            url = make_link_absolute(url_text, "https://www.washingtonpost.com/politics")
            if url.startswith("https://www.washingtonpost.com/politics"):
                article.add(url)
            else:
                video.add(url)
        begin = base_page.find("offset") + 9
        end = base_page.find("%26limit")
        try:
            articlenumber = int(base_page[begin:end])
        except ValueError:
            articlenumber = 10000
        if articlenumber < 9960:
            articlenumber += 30
            articlenumber = str(articlenumber)
            rev_basepage = (
                base_page[0:begin] + articlenumber + base_page[end : (len(base_page) + 1)]
            )
            article, video = self.crawl(rev_basepage, article, video)
        return article, video

class WashingtonPost(WaybackCrawler):
        def __init__(self):
            super().__init__()
            self.start_url = 'https://www.washingtonpost.com/politics/'
            self.selector = ['div.story-headline.pr-sm']
        def get_archive_urls(self, url, selectors):
            articles=super().get_archive_urls(url, selectors)
            filtered_articles = [article for article in articles if "https://www.washingtonpost.com/politics/2" in article]
            return filtered_articles

    






       
