from ..crawler import WaybackCrawler
from newsfaces.extract_html import Extractor
from newsfaces.utils import make_link_absolute
import lxml.html
from ..models import URL, Image, ImageType
from wayback import memento_url_data


class APArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("ap")
        self.start_url = ""
        self.selector = []

    def get_article_urls(self, response):
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
        doc = lxml.html.fromstring(response.text)
        selectors = [
            "div.FourColumnContainer-column",
            "div.TwoColumnContainer7030",
            "div.PageList-items",
            "div.storyContainer"

        ]
        for a in selectors:
            container = doc.cssselect(a)
            if len(container) > 0:
                yield from self.parse_links(container)
        xpath_sel = ["TwoColumnContainer", "CardHeadline","primaryContent", "article-layout"]
        # for items that have random characters continually added at the end so we do
        # non-exact matching
        for j in xpath_sel:
            container = doc.xpath(f"//div[contains(@class, '{j}')]")
            if len(container) > 0:
                yield from self.parse_links(container)

    def parse_links(self, container):
        """
        Takes a list of container objects and returns the urls
        from within
        """
        for j in container[0]:
            atr = j.cssselect("a")
            for a in atr:
                href = a.get("href")
                if href is not None:
                    if href.startswith("/web/"):
                        href = make_link_absolute(href, "https://web.archive.org")
                        clean_href = memento_url_data(href)[0]
                    yield URL(url=clean_href, source=self.source_name)
    
    def get_wayback_urls(self, when: str):
        urls= ["https://apnews.com/hub/politics", "https://apnews.com/politics",
            "https://apnews.com/tag/apf-politics", "http://bigstory.ap.org/on-the-campaign-trail"]
        for i in range(len(urls)):
            self.start_url = urls[i]
            yield from super().get_wayback_urls(when)

class AP_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["main.Page-main"]
        self.img_p_selector = ["figure.Figure"]
        self.img_selector = ["img"]
        self.head_img_div = ["div.CarouselSlide"]
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1.Page-headline"]

    def extract_head_img(self, html, img_p_selector, img_selector):
        """
        Extract the image content from parsed HTML:
        Inputs:
            - html(str): Html from HTTP request
            - img_p_selector(list): css selector for the parent elements of images
            - img_selector(list): list of css selector for the image elements
            Return:
            -imgs(lst): list where each element is an image represented as a dictionary
            with src, alt, title, and caption as fields
        """
        imgs = []
        for selector in img_p_selector:
            img_container = html.cssselect(selector)
            if len(img_container) == 0:
                continue
            for container in img_container:
                for j in img_selector:
                    photos = container.cssselect(j)
                    for i in photos:
                        caption_text = self.get_img_caption(i)
                        img_item = Image(
                            url=i.get("data-flickity-lazyload") or "",
                            image_type=ImageType("main"),
                            caption=caption_text,
                            alt_text=i.get("alt") or "",
                        )
                        imgs.append(img_item)
                    break

        return imgs
    
    