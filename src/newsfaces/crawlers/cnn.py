import re
import lxml.html
import requests
import datetime
import pytz
from databeakers.http import HttpResponse
from ..crawler import WaybackCrawler
from ..utils import make_link_absolute
from ..models import URL, Image, ImageType
from ..extract_html import Extractor
from typing import Generator

# The results for https://cnn.com/politics have different types of answers
# depending on the date so we need to create additional datetime objects to deal
# with different periods
# I) 2015 - Oct 18 2016: Archive works ok, no Java Script
# II) Oct 18 2016 - Jan 30 2017: Internet Archive result does not work. There
# is a CNN loading logo but no urls appear
# III) Jan 31st 2017 - Dec 13 2022: Archive works ok, uses Java Script
# IV) Dec 13 2022 - present: Archive works ok, no Java Script

# Date of first archived with JS
JS_START_DATE = datetime.datetime(2017, 1, 31, 6, 39, 53, tzinfo=pytz.timezone("utc"))
# Date of first archived without JS
JS_END_DATE = datetime.datetime(2022, 12, 13, 0, 33, 15, tzinfo=pytz.timezone("utc"))
# Date of first archived with no results
STOP_WORKING_DATE = datetime.datetime(
    2016, 10, 18, 17, 41, 32, tzinfo=pytz.timezone("utc")
)


class CnnArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("cnn")
        self.start_url = "https://www.cnn.com/politics/"
        self.selector = ["div.container__item", "h3.cd__headline"]
        self.session_js = requests.Session()

    def get_archive_urls_js(self, time_str):
        urls = []
        json_url = (
            f"https://web.archive.org/web/{time_str}/"
            "https://www.cnn.com/data/ocs/section/politics/index.html:"
            "politics-zone-1/views/zones/common/zone-manager.izl"
        )
        resp = self.session_js.get(json_url)
        resp_json = resp.json()
        html = lxml.html.fromstring(resp_json["html"])

        article_elements = html.cssselect("h3.cd__headline")
        article_link = article_elements[0].cssselect("a")[0].get("href")
        article_link

        for article in article_elements:
            try:
                rel_link = article.cssselect("a")[0].get("href")
            except IndexError:
                continue
            absolute_link = make_link_absolute(rel_link, "https://www.cnn.com")

            urls.append(URL(url=absolute_link, source=self.source_name))

        return urls

    def get_article_urls(self, response: HttpResponse) -> Generator[URL, None, None]:
        time_str = re.findall(r"(\d{14})", response.url)[0]
        time_stamp = datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S").astimezone(
            pytz.timezone("utc")
        )
        if JS_START_DATE < time_stamp < JS_END_DATE:
            yield from self.get_archive_urls_js(time_str)
        else:
            yield from super().get_article_urls(response)


class CNNExtractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["main.article__main"]
        self.article_body = ["div.article__content-container"]
        # self.img_p_selector = ["div.image__container"]
        self.img_p_selector = [
            """//div[@class="figure-container"]
                               [not(ancestor::div[@class="related-content__image"])]"""
        ]
        self.img_selector = ["img"]
        self.p_selector = ["p.paragraph"]
        self.t_selector = ["h1.headline__text"]
        self.head_img_select = ["img"]
        self.head_img_div = ["picture.image__picture"]

    def extract_head_img(self, html, img_p_selector, img_selector):
        """
        Extract the image content from an HTML:
        Inputs:
            - html(str): html to extract images from
            - img_p_selector(list): css selector for the parent elements of images
            - img_selector(list): list of css selector for the image elements
            Return:
            -imgs(lst): list where each element is an image represented as a
            dictionary
            with src, alt, title, and caption as fields
        """
        caption_selectors = ["div.video-resource__headline", "span.inline-placeholder"]
        body = html.cssselect("div.image__lede")[0]
        img_container = body.cssselect(img_p_selector[0])

        # Check if there exists an img_container for head image
        if img_container:
            # Both the caption and head image live inside the same parent element
            # a.Grab img:
            head_img = img_container[0].cssselect(img_selector[0])[0]
            # Grab caption:
            # b.
            for cap_s in caption_selectors:
                cap_el = body.cssselect(cap_s)
                if cap_el:
                    caption_t = cap_el[0].text_content()
                    break
                else:
                    caption_t = ""

            img_item = Image(
                url=head_img.get("src") or "",
                image_type=ImageType("main"),
                caption=caption_t,
                alt_text=head_img.get("alt") or "",
            )
            return [img_item]
        else:
            return []

    def extract_imgs(self, html, img_p_selector, img_selector):
        imgs = []

        caption_selector = "span.inline-placeholder"

        # a.Save img items
        #
        # img_containers = html.cssselect(img_p_selector[0])
        img_containers = html.xpath(img_p_selector[0])
        img_elements = []
        if img_containers:
            for container in img_containers:
                img_elements.append(container.cssselect(img_selector[0])[0])

        # b.save captions
        caption_el = html.cssselect(caption_selector)
        captions = []
        if caption_el:
            for caption in caption_el:
                caption_t = caption.text_content()
                captions.append(caption_t)

        # Only match captions if there are as many captions as img_elements
        if len(img_elements) == len(captions):
            for i in range(len(img_elements)):
                img_item = Image(
                    url=img_elements[i].get("src") or "",
                    image_type=ImageType("main"),
                    caption=captions[i] or "",
                    alt_text=img_elements[i].get("alt") or "",
                )
                imgs.append(img_item)
        else:
            for i in img_elements:
                img_item = Image(
                    url=img_elements[i].get("src") or "",
                    image_type=ImageType("main"),
                    caption="",
                    alt_text=img_elements[i].get("alt") or "",
                )
                imgs.append(img_item)

        return imgs
