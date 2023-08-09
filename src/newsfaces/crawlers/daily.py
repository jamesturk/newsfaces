import re
import datetime
from .crawler import Crawler
from ..utils import make_link_absolute, page_grab
from ..extract_html import Extractor 
from ..models import Image, ImageType

CURRENT_YEAR = datetime.datetime.now().year

class DailyCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://dailycaller.com/section/politics/"
        self.prefix = "https://dailycaller.com/"

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
            full_link = make_link_absolute(link, self.prefix)
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

    def crawl(self, start_date=datetime.date(2015,1,1)):
        """
        Starting from 2023 it fetches the urls of the daily caller politics section
        """
        min_year = start_date.year
        years = list(range(min_year, CURRENT_YEAR+1, 1))
        page = 1
        articles_set = set()
        for year in reversed(years):
            print("Obtainings links for", year)
            year_set, page = self.obtain_year_urls(page, year)
            articles_set.update(year_set)
            page += 1

        return articles_set

class DailyExtractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div.article-content-wrap.sticky-columns"]
        self.img_p_selector = ["div.m"]
        self.img_selector = ["img"]
        self.head_img_div = ["div.contain"]
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1"]
    
    def extract_head_img(self, html, img_p_selector, img_selector):
        """
        Extract the image content from an HTML:
        Inputs:
            - html(str): html to extract images from
            - img_p_selector(list): list of css selector for the parent elements of images in articles
            - img_selector(list): list of css selector for the image elements
            Return:
            -imgs(lst): list where each element is an image represented as a dictionary
            with src, alt, title, and caption as fields
        """

        img_container = html.cssselect(img_p_selector[0])[0]
        head_img = img_container.cssselect(img_selector[0])[0]

        img_item = Image(
                        url=head_img.get("data-src") or "",
                        image_type=ImageType("main"),    
                        caption=head_img.get("caption") or "",
                        alt_text=head_img.get("alt") or "",
                        )
                    
        return [img_item]
    
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

        #Daily has only one image selector over the years, so avoid iterating
        img_container = html.cssselect(img_p_selector[0])

        #Obtain img info and captions which in the Daily both live inside the
        #same parent element (img_container)
        for container in img_container:
            caption= container.cssselect("p.wp-caption-text")[0].text 
            for j in img_selector:
                photos = container.cssselect(j)
                for i in photos:
                    img_item = Image(
                        url=i.get("src") or "",
                        image_type=ImageType("main"),
                        caption=caption or "",
                        alt_text=i.get("alt") or "",
                    )
                imgs.append(img_item)
        
        return imgs
