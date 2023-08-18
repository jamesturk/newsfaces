import datetime
from newsfaces.models import URL
from ..crawler import Crawler
from ..utils import make_link_absolute
from ..extract_html import Extractor
from ..models import Image, ImageType

CURRENT_YEAR = datetime.datetime.now().year


class Done(Exception):
    pass


class DailyCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.url = "https://dailycaller.com/section/politics/"
        self.prefix = "https://dailycaller.com/"
        self.source = "daily"

    def obtain_page_urls(self, page="1"):
        """
        Obtain the urls of the politics section of a url in the Daily Caller politics
        section

        Inputs:
            - page(str): page of the politics section to fetch urls
        Yields:
            - url(URl): url of the article
            - year(str): year of the article
        """
        url = self.url + "page/{}/".format(page)
        root = self.make_request(url)
        article_elements = list(root.cssselect("article.relative"))
        if not article_elements:
            raise Done()

        for article in article_elements:
            link = article.cssselect("a")[0].get("href")
            # Some articles in the Daily Caller politcs section
            # Are articles from another webpage checkyourfact and we will drop these
            if link.startswith("http://checkyourfact"):
                continue
            full_link = make_link_absolute(link, self.prefix)
            yield URL(url=full_link, source=self.source)

    def crawl(self, start_date=datetime.date(2015, 1, 1)):
        """
        Starting from 2023 it fetches the urls of the daily caller politics section
        """
        page = 1
        while True:
            print("Obtaining results for page", page)
            try:
                yield from self.obtain_page_urls(str(page))
            except Done:
                break
            page += 1


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
            - img_p_selector(list): list of css selector for the parent elements
              of images in articles
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
            - img_p_selector(list): list of css selector for the parent elements
              of images in articles
            - img_selector(list): css selector for the image elements
            Return:
            -imgs(lst): list where each element is an image represented as
            an image object
        """
        imgs = []

        # Daily has only one image selector over the years, so avoid iterating
        img_container = html.cssselect(img_p_selector[0])

        # Obtain img info and captions which in the Daily both live inside the
        # same parent element (img_container)
        for container in img_container:
            caption = container.cssselect("p.wp-caption-text")[0].text
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
