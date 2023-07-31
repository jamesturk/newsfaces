from .crawler import Crawler, WaybackCrawler
from newsfaces.utils import make_link_absolute


class BBC_Latest(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.bbc.com/news/topics/cwnpxwzd269t?page=1"
    
    def crawl(self):
        '''
        run get_html with correct initial html from init
        '''
        return self.get_html(self.start_url)
    
    def get_html(self, url, articles=set(), videos=set()):
        """
        Takes an initial url and runs get_urls on all possible
        API queries. Gathering all possible articles and videos
        from the API into a set.
        """
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
                articles.add(href)
            elif type == "video":
                videos.add(href)
        return articles, videos


class BBC(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.bbc.com/news/topics/cwnpxwzd269t"
        self.selector = ["div.archive__item__content", "h2.node__title.node-title"]

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
                href = make_link_absolute(href, " https://web.archive.org")
            if type == "article":
                articles.add(href)
            elif type == "video":
                videos.add(href)
        return articles.union(videos)
