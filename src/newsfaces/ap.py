from urllib.parse import urlparse
from utils import page_grab, make_link_absolute
def get_urls_ap(url):
    """
    This function takes a URLs and returns lists of URLs
    for containing each article on that page.

    Parameters:
        * url:  a URL to a page of articles
        * session: optional session object parameter
        * selectors: a list of css selectors

    Returns:
        A list of article URLs on that page.
    """
    response = page_grab(url)
    urls = []
    selectors=['div.FourColumnContainer-column','div.TwoColumnContainer7030','div.PageList-items','article']
    for a in selectors:
        container=response.cssselect(a)
        if len(container)>0:
            for j in container[0]:
                atr = j.cssselect("a")
                for a in atr:
                    href = a.get("href")
                    if href.startswith('/web/'):
                         href = make_link_absolute(href, "https://web.archive.org")
                    if href is not None:
                        urls.append(href)
    return urls