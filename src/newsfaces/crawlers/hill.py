from ..models import Image, ImageType
from ..crawler import WaybackCrawler
from ..extract_html import Extractor



class TheHillArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("hill")
        self.start_url = "https://thehill.com/policy/"
        self.selector = ["div.archive__item__content", "h2.node__title.node-title"]


class Hill_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div.article__text.|.body-copy.|.flow"]
        self.img_p_selector = ['figure[class^="wp-block-image"]']
        self.img_selector = ["img"]
        self.head_img_div = ["figure.article__featured-image"]
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1"]

    def extract_imgs(self, html, img_p_selector, img_selector):
        """
        Extract the image content from an HTML:
        Inputs:
            - html(str): html to extract images from
            - img_p_selector(list): css selector for the parent elements of images
            - img_selector(list): css selector for the image elements
            Return:
            -imgs(lst): each element is an image represented as an image object
        """
        imgs = []
        for selector in img_p_selector:
            img_container = html.cssselect(selector)
            if len(img_container) == 0:
                continue
            for container in img_container:
                for j in img_selector:
                    photos = container.cssselect(j)
                    for photo in photos:
                        caption= photo.xpath('ancestor::figure/figcaption')
                        if caption:
                            cap_text = caption[0].text_content()
                        else:
                            cap_text = ""
                        img_item = Image(
                            url=photo.get("src") or "",
                            image_type=ImageType("main"),
                            caption= cap_text, 
                            alt_text=photo.get("alt") or "",
                        )
                        imgs.append(img_item)
        return imgs