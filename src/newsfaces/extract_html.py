from newsfaces.models import Article, Image, ImageType


class Extractor(object):
    def __init__(self):
        self.article_body = []
        self.img_p_selector = []
        self.img_selector = ["img"]
        self.head_img_div = []
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = []

    def extract_html(self, http):
        """
        Extract the image and text content from and HTTP:
        Inputs:
            - HTTP(str): Full HTTP request of an article url
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
            if len(http.cssselect(selector)[0]) > 0:
                article_body = http.cssselect(selector)[0]
                break
        if self.head_img_div:
            imgs += self.extract_head_img(http, self.head_img_div, self.head_img_select)
        imgs += self.extract_imgs(article_body, self.img_p_selector, self.img_selector)
        imgs += self.extract_social_media_image(http)
        art_text = self.extract_text(article_body, self.p_selector)

        for t in self.t_selector:
            if http.cssselect(t)[0].text is not None:
                t_text = http.cssselect(t)[0].text
                break
        return imgs, art_text, t_text

    def extract_text(self, http, p_selector):
        """
        Extract the article text content from an HTTP Request:
        Inputs:
            - p_selector(list): css selectors for paragraphs living
              inside the article container
        Return:
            - text(str): Article text
        """
        text = ""
        if p_selector:
            for p in p_selector:
                paragraphs = http.cssselect(p)
                if paragraphs:
                    for p in paragraphs:
                        text += p.text_content()
                    break

        return text

    def extract_head_img(self, http, img_p_selector, img_selector):
        """
        Extract the image content from an HTTP request:
        Inputs:
            - http(str): HTTP Request
            - img_p_selector(list): css selector for the parent elements of images
            - img_selector(list): list of css selector for the image elements
            Return:
            -imgs(lst): list where each element is an image represented as a dictionary
            with src, alt, title, and caption as fields
        """
        for selector in img_p_selector:
            img_container = http.cssselect(selector)
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
        try:
            return [img_item]
        except UnboundLocalError:
            return

    def extract_imgs(self, http, img_p_selector, img_selector):
        """
        Extract the image content from an HTTP Request:
        Inputs:
            - HTTP(str): http to extract images from
            - img_p_selector(list): css selector for the parent elements of images
            - img_selector(list): css selector for the image elements
            Return:
            -imgs(lst): each element is an image represented as an image object
        """
        imgs = []
        for selector in img_p_selector:
            img_container = http.cssselect(selector)
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
                        imgs.append(img_item)
        return imgs

    def extract_social_media_image(self, http):
        container = http.cssselect('meta[property="og:image"]')
        img_item = Image(
            url=container[0].get("content"),
            image_type=ImageType("social"),
            caption="",
            alt_text="",
        )
        return [img_item]

    def scrape(self, http):
        """
        Return article object from http request
        """
        imgs, art_text, t_text = self.extract_html(http)
        article = Article(title=t_text or "", article_text=art_text or "", images=imgs)
        return article
