from ..crawler import WaybackCrawler
from ..utils import make_link_absolute
from ..models import Image, ImageType
from ..extract_html import Extractor
import lxml.html


class BreitbartArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("breitbart")
        self.start_url = "https://www.breitbart.com/politics/"
        self.selector = ["article"]

    def get_archive_urls(self, response):
        doc = lxml.html.fromstring(response.text)
        urls = []
        article_elements = doc.cssselect("article")
        for article in article_elements:
            atr = article.cssselect("a")
            if atr and len(atr) > 0:
                href = atr[0].get("href")
                if len(href) > 0:
                    urls.append(make_link_absolute(href, "https://web.archive.org/"))
        return urls
    
class BreitbartExtractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["article.the-article"]
        self.img_p_selector = ["div.wp-caption.alignnone"]
        self.img_selector = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1"]
        self.head_img_select = ["img"]
        self.head_img_div = ["figure"]
    
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
        body = html.cssselect("header")[0]
        img_container = body.cssselect(img_p_selector[0])

        #Check if there exists an img_container for head image
        if img_container:
            #Both the caption and head image live inside the same parent element
            head_img = img_container[0].cssselect(img_selector[0])[0]
            caption_el = img_container[0].cssselect("cite")[0]
        
            img_item = Image(url=head_img.get("src") or "",
                        image_type=ImageType("main"),
                        caption=caption_el.text_content() or "",
                        alt_text=head_img.get("alt") or "",
                        )
            return [img_item]
        else:
            print("None container for header image found")
            return []
        
    def extract_imgs(self, html, img_p_selector, img_selector):
        imgs = []
        img_container = html.cssselect(img_p_selector[0])
        for item in img_container:
            img = item.cssselect(img_selector[0])[0]
            caption = item.cssselect("p.wp-caption-text")[0]
            img_item = Image(
                            url=img.get("src") or "",
                            image_type=ImageType("main"),
                            caption=caption.text_content() or "",
                            alt_text=img.get("alt") or "",
                        )
            imgs.append(img_item)
        return imgs
