# TODO: add annotation to scrape() once RateLimit properly handles the wrapped annotation
from databeakers.http import HttpResponse
from newsfaces.models import Article, Image, ImageType
import lxml.html


class MissingBodyError(Exception):
    pass


class Extractor:
    def __init__(self):
        self.article_body = []
        self.img_p_selector = []
        self.img_selector = ["img"]
        self.head_img_div = []
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = []

    def extract_html(self, html):
        """
        Extract the image and text content from and Html:
        Inputs:
            - Html(str): Full Parsed Html of an article url
            - article_selector(str): css selector for article container
            - head_img_div(list)- css selector for parent div of headline image
            - head_img_select(list)- css selector for images
            - img_p_selector(list): css selector for the parent elements of images
            - img_selector(list): css selector for images living inside the article
            container
            - p_selector(list): css selector for paragraphs living inside the
                                article container
            - t_selector(list): css selector for title living inside the container
        Return:
            -imgs(lst): list where each element is an instance of a Image Class
            - art_text(str): Article text
            - t_text(str): Title
        """
        t_text = ""
        art_text = []
        imgs = []

        for selector in self.article_body:
            results = html.cssselect(selector)
            if len(results):
                article_body = results[0]
                break
        else:
            raise MissingBodyError(
                f"No article body found selector={self.article_body}"
            )
        if self.head_img_div:
            imgs += self.extract_head_img(html, self.head_img_div, self.head_img_select)
        imgs += self.extract_imgs(article_body, self.img_p_selector, self.img_selector)
        imgs += self.extract_social_media_image(html)
        imgs += self.get_video_imgs(html)
        art_text = self.extract_text(article_body, self.p_selector)

        for t in self.t_selector:
            results = html.cssselect(t)
            if len(results):
                t_text = results[0].text
                break
        return imgs, art_text, t_text

    def extract_text(self, html, p_selector):
        """
        Extract the article text content from an parsed HTML string:
        Inputs:
            - p_selector(list): css selectors for paragraphs living
              inside the article container
        Return:
            - text(str): Article text
        """
        text = ""
        if p_selector:
            for p in p_selector:
                paragraphs = html.cssselect(p)
                if paragraphs:
                    for p in paragraphs:
                        text += p.text_content()
                    break

        return text

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
                            url=i.get("src") or "",
                            image_type=ImageType("main"),
                            caption=caption_text,
                            alt_text=i.get("alt") or "",
                        )
                        imgs.append(img_item)
                    break

        return imgs

    def extract_imgs(self, html, img_p_selector, img_selector):
        """
        Extract the image content from an HTTP Request:
        Inputs:
            - html(str): parsed html string to extract images from
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
                    for i in photos:
                        caption_text = self.get_img_caption(i)
                        img_item = Image(
                            url=i.get("src") or "",
                            image_type=ImageType("main"),
                            caption=caption_text or "",
                            alt_text=i.get("alt") or "",
                        )
                        imgs.append(img_item)
        return imgs

    def extract_social_media_image(self, html):
        """
        extract social media tagged meta image
        input:
        html (parsed string)- page html
        returns: image object
        """
        container = html.cssselect('meta[property="og:image"]')
        if container:
            img_item = Image(
                url=container[0].get("content"),
                image_type=ImageType("social"),
                caption="",
                alt_text="",
            )
            return [img_item]
        else:
            return []

    def get_img_caption(self, img):
        """
        if img has a figure attribute, get the related figure caption
        input: image-parsed html for inage tage
        output: figure caption text

        """
        figcaption = img.xpath("ancestor::figure/figcaption | //figcaption")
        if figcaption:
            caption_text = figcaption[0].text_content().strip()
        else:
            caption_text = ""
        return caption_text

    def get_video_imgs(self, html):
        return []

    def scrape(self, response: HttpResponse) -> Article | None:
        """
        Return article object from html string request
        """
        if response.status_code < 400:
            html = lxml.html.fromstring(response.text)
            imgs, art_text, t_text = self.extract_html(html)
            article = Article(
                title=t_text or "", article_text=art_text or "", images=imgs
            )
            return article
        else:
            return None
