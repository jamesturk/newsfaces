# Util Functions
from urllib.parse import urlparse
from crawlers.utils import make_link_absolute, page_grab


def get_urls(url):
    """
    This function takes a URLs and returns lists of URLs
    for containing each article on that page.

    Parameters:
        * url:  a URL to a page of articles

    Returns:
        A list of article URLs on that page.
    """
    response = page_grab(url)
    urls = []
    container = response.cssselect("div.summary")

    for j in container:
        atr = j.cssselect("a")
        if atr and len(atr) > 0:
            href = atr[0].get("href")
            urls.append(make_link_absolute(href, "https://www.politico.com"))
    return urls


def recurse_politico(url, breakpoint, urls=[]):
    """
    Runs get_url's function on all possible article landing pages
    until a specific page (breakpoint). Returns a list of article
    urls across pages
    """
    scraped_urls = get_urls(url)
    urls += scraped_urls
    begin = url.find("politics/") + 9
    pagenumber = int(url[begin : len(url)])
    if pagenumber < breakpoint:
        newlink = url[: -len(str(pagenumber))] + str(pagenumber + 1)
        recurse_politico(newlink, breakpoint, urls)
    return urls


def politico_get_urls():
    urllist = []
    urllist2 = []
    urllist = recurse_politico("https://www.politico.com/politics/1", 1700)
    urllist2 = recurse_politico("https://www.politico.com/politics/1700", 3400)
    pooled = set(urllist + urllist2)
    return pooled


class Politico(Crawler):
    def __init__(self):
        super().__init__()

    def crawl(self):
        """
        Implement crawl here to override behavior
        """
        return politico_get_urls()
