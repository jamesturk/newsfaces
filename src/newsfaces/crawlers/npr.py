import re
import datetime
from .crawler import Crawler
from ..extract_html import Extractor
from models import Image, ImageType

CURRENT_YEAR = datetime.datetime.now().year


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

    def crawl(self, start_time=datetime.date(2015, 1, 1)):
        """
        Crawl the NPR politics section
        Inputs:
        - min_year(int): Oldest year to get results from
        Return:
        - npr_url(set): Set of all the NPR politics section url until the specified year
        """
        min_year = start_time.year
        articles_set = set()
        for year in range(min_year, CURRENT_YEAR + 1):
            for month in range(1, 13):
                articles_set.update(self.obtain_monthly_urls(0, month, year))

        return articles_set


class NPRExtractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["article.story"]
        self.img_p_selector = ["div.imagewrap"]
        self.img_selector = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1"]
        self.head_img_select = []

    def extract_imgs(self, html, img_p_selector, img_selector):
        """
        Extract the image content from an HTML:
        Inputs:
            - html(str): html to extract images from
            - img_p_selector(list): list of css selector for the parent elements of images in articles
            - img_selector(list): css selector for the image elements
            Return:
            -imgs(lst): list where each element is an image represented as an image object
        """
        imgs = []
        img_items = []
        captions = []

        # Add images src and alt text
        for selector in img_p_selector:
            img_container = html.cssselect(selector)
            for container in img_container:
                for j in img_selector:
                    photos = container.cssselect(j)
                    for i in photos:
                        # Most NPR images don't have alt text so to avoid
                        # problems when iterating and indexing the list, we add it in a
                        "dictionary"
                        img_item = {"src": i.get("src"), "alt": i.get("alt")}

                    img_items.append(img_item)

        # Create captions list that live in other elements
        caption_items = html.cssselect("div.caption")
        for item in caption_items:
            caption = item.cssselect("p")[0].text
            captions.append(caption)

        # Create image items joining each caption with their respective image
        for i in range(len(img_items)):
            image = Image(
                url=img_items[i]["src"] or "",
                image_type=ImageType("main"),
                alt_text=img_items[i]["alt"] or "",
                caption=captions[i],
            )
            imgs.append(image)

        return imgs
