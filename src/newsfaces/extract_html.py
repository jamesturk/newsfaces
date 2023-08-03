
from newsfaces.utils import page_grab
from newsfaces.models import Article, Image, ImageType


class Extractor(object):
    def __init__(self):
        self.html = ""
        self.article_body = []
        self.img_p_selector = []
        self.img_selector = ["img"]
        self.head_img_div = []
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = []

    def extract_html(self):
        """
        Extract the image and text content from and HTML:
        Inputs:
            - html(str): Full html of an artcile url
            - article_selector(str): css selector for article container
            - head_img_div(list)- css selector for parent div of headline image
            - head_img_select(list)- css selector for images
            - img_p_selector(list): css selector for the parent elements of images in article
            - img_selector(list): css selector for images living inside the article
            container
            - p_selector(list): css selector for paragraphs living inside the article container
            - t_selector(list): css selector for title living inside the container
        Return:
            -imgs(lst): list where each element is an image represented as a dictionary
            with src, alt, title, and caption as fields
            - art_text(str): Article text
            - t_text(str): Title
        """
        t_text = ""
        art_text = []
        imgs = []

        for selector in self.article_body:
            if len(self.html.cssselect(selector)[0]) > 0:
                article_body = self.html.cssselect(selector)[0]
                break
        if self.head_img_select:
            imgs += self.extract_head_img(
                self.html, self.head_img_div, self.head_img_select
            )
        imgs += self.extract_imgs(article_body, self.img_p_selector, self.img_selector)
        art_text = self.extract_text(article_body, self.p_selector)
        for t in self.t_selector:
            if self.html.cssselect(t)[0].text is not None:
                t_text = self.html.cssselect(t)[0].text
                break
        return imgs, art_text, t_text

def extract_html(
    html, article_selector,img_p_selector, img_selector="img", p_selector=None,
    t_selector=None):
    """
    Extract the image and text content from and HTML:
    Inputs:
        - html(str): Full html of an artcile url
        - article_selector(str): css selector for article container
        - img_p_selector(str): css selector for the parent elements of images in article
        - img_selector(str): css selector for images living inside the article
        container
        - p_selector(str): css selector for paragraphs living inside the article container
        - t_selector(str): css selector for title living inside the article container
    Return:
        -imgs(lst): list where each element is an image represented as a dictionary
        with src, alt, title, and caption as fields
        - art_text(str): Article text
        - t_text(str): Title
    """
    article_body = html.cssselect(article_selector)[0]
    imgs = extract_imgs(article_body,img_p_selector,img_selector)
    art_text = extract_text(article_body, p_selector)
    if t_selector:
        t_text = html.cssselect(t_selector)[0].text
    return imgs, art_text, t_text

def extract_imgs(html, img_p_selector,img_selector="img"):
    """
    Extract the image content from an HTML:
    Inputs:
        - html(str): html to extract images from
        - img_p_selector(list): list of css selector for the parent elements of images in articles
        - img_selector(str): css selector for the image elements
        Return:
        -imgs(lst): list where each element is an image represented as a dictionary
        with src, alt, title, and caption as fields
    """
    imgs = []
    for selector in img_p_selector:
        img_container = html.cssselect(selector)
        for container in img_container:
            images = container.cssselect(img_selector)
            for img in images:
                img_item = {}
                img_item["src"] = img.get("src")
                img_item["alt"] = img.get("alt")
                img_item["title"] = img.get("title")
                img_item["caption"] = img.get("caption")
                imgs.append(img_item)
    return imgs


    def extract_text(self, html, p_selector):
        """
        Extract the article text content from an HTML:
        Inputs:
            - p_selector(list): css selectors for paragraphs living inside the article container
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
        Extract the image content from an HTML:
        Inputs:
            - html(str): html to extract images from
            - img_p_selector(list): list of css selector for the parent elements of images in articles
            - img_selector(list): list of css selector for the image elements
            Return:
            -imgs(lst): list where each element is an image represented as a dictionary
            with src, alt, title, and caption as fields
        """
        for selector in img_p_selector:
            img_container = html.cssselect(selector)
            if len(img_container) == 0:
                continue
            for container in img_container:
                for j in img_selector:
                    photos = container.cssselect(j)
                    for i in photos:
                        img_item = Image(
                            url=i.get("src") or "",
                            image_type=ImageType("main"),
                            caption=i.get("caption") or "",
                            alt_text=i.get("alt") or "",
                        )
                    break
        return [img_item]

    def scrape(self):
        imgs, art_text, t_text = self.extract_html()
        article = Article(title=t_text or "", article_text=art_text or "", images=imgs)
        return article


class Fox_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.html = page_grab(
            "https://www.foxnews.com/politics/kerry-ripped-demanding-agriculture-emission-cuts-bankrupt-every-farmer"
        )
        self.article_body = ["div.article-content-wrap.sticky-columns"]
        self.img_p_selector = ["div.m"]
        self.img_selector = ["img"]
        self.head_img_div = ["div.contain"]
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1", "h6"]

    def extract_head_img(self, html="", img_p_selector="", img_selector=""):
        return []


a = Fox_Extractor()
a.scrape()
