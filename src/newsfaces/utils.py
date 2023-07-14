# Util Functions
import time
import requests
from urllib.parse import urlparse
import sys
import json
import lxml.html
import csv
from wayback import WaybackClient, memento_url_data, WaybackSession
import itertools
import datetime

REQUEST_DELAY = 0.2


def make_request(url, session=None):
    """
    Make a request to `url` and return the raw response.

    This function ensure that the domain matches what is expected and that the rate limit
    is obeyed.
    """
    # check if URL starts with an allowed domain name
    time.sleep(REQUEST_DELAY)
    print(f"Fetching {url}")
    if session:
        resp = session.get(url)
    else:
        resp = requests.get(url)
    return resp


def make_link_absolute(rel_url, current_url):
    """
    Given a relative URL like "/abc/def" or "?page=2"
    and a complete URL like "https://example.com/1/2/3" this function will
    combine the two yielding a URL like "https://example.com/abc/def"

    Parameters:
        * rel_url:      a URL or fragment
        * current_url:  a complete URL used to make the request that contained a link to rel_url

    Returns:
        A full URL with protocol & domain that refers to rel_url.
    """
    url = urlparse(current_url)
    if rel_url.startswith("/"):
        return f"{url.scheme}://{url.netloc}{rel_url}"
    elif rel_url.startswith("?"):
        return f"{url.scheme}://{url.netloc}{url.path}{rel_url}"
    else:
        return rel_url


def parse_html(html):
    """
    Parse HTML and return the root node.
    """
    return lxml.html.fromstring(html)


def page_grab(url, session=None):
    response = make_request(url, session)
    root = parse_html(response.text)
    return root


def create_csv(set1, title1, filename, set2=set(), title2=""):
    """
    turns list of articles and videos into a csv with
    these values as respective columns.
    args:
    set1- items scraped (ex. article urls)
    set2- second type of items scraped (ex. videos)
    title1- column header for first type
    title2- optional header for second type
    """
    with open(filename, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow([title1, title2])
        max_length = max(len(set1), len(set2))
        for i in range(max_length):
            row = [
                list(set1)[i] if i < len(set1) else "",
                list(set2)[i] if i < len(set2) else "",
            ]
            writer.writerow(row)


def get_urls(url, selectors, session=None):
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
    response = page_grab(url, session)
    urls = []
    for selector in selectors:
        container = response.cssselect(selector)
        for j in container:
            atr = j.cssselect("a")
            if atr and len(atr) > 0:
                href = atr[0].get("href")
                if len(href) > 0:
                    urls.append(make_link_absolute(href, "https://web.archive.org/"))
    return urls


def crawl_wayback(homepage, break_point, scraper_func, startdate, selectors=False):
    """
    Take a politics homepage, or any source with a list of articles, finds all
    copies in the archive, and scrapes all of the article links on that page.
    args:
        homepage- the homepage or politics page we are looking for across time
        break_point- the approx. number of copies in the archive
        scraper_func - the individual function built for scraping that page
        startdate- the date you would like to begin scraping ('YYYYMMDD')
        selectors- optional css selector parameter(to be used with scraper_func)
    returns:
        list of articles from startdate to present

    """
    session = WaybackSession()
    client = WaybackClient(session)
    results = client.search(homepage, match_type="exact", from_date=startdate)
    crosstime_urls = list(itertools.islice(results, break_point))
    post_date_articles = set()
    for i in range(len(crosstime_urls)):
        date = datetime.datetime.strptime(startdate, "%Y%m%d")
        if crosstime_urls[i].timestamp.date() >= date.date():
            if selectors:
                articles = scraper_func(crosstime_urls[i].view_url, selectors, session)
            else:
                articles = scraper_func(crosstime_urls[i].view_url, session)
            # converts archive links back to current article links
            articles = [memento_url_data(item)[0] for item in articles]
            post_date_articles.update(articles)
    return post_date_articles
