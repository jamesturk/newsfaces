from ..crawler import Crawler
from ..extract_html import Extractor
from ..models import Image, ImageType, URL
from ..utils import page_grab, make_link_absolute
import datetime

CURRENT_YEAR = datetime.datetime.now().year


class NewsmaxCrawler(Crawler):
    def __init__(self, min_year=2016):
        super().__init__()
        self.url = "https://www.newsmax.com/archives/politics/1/"
        self.min_year = min_year
        self.source = "newsmax"

    def obtain_page_urls(self, year="2016", month="1"):
        """
        Obtain the urls for a given year and month from the politics
        section of Newsmax
        Inputs:
        -year(str): Year of the articles to search for
        -month(str): Month of the articles to search for
        Return:
        links_list(list): List of urls
        """
        url = self.url + "{}/{}/".format(year, month)
        root = self.make_request(url)
        links_elements = root.cssselect("h5.archiveH5")
        for element in links_elements:
            link = element.cssselect("a")
            href = make_link_absolute("https://newsmax.com", link[0].get("href"))
            yield URL(url=href, source=self.source)

    def crawl(self):
        """
        Obtain all newsmax urls from the politics section
        Inputs: None
        Return:
        newsmax_links (dict): Dictionary where the keys are str for
          date (year-mth)
        and values are lists with the urls of that given key
        """
        for year in range(self.min_year, CURRENT_YEAR + 1):
            for month in range(1, 13):
                date = str(year) + "-" + str(month)
                print("Obtaining news from:", date)
                yield from self.obtain_page_urls(str(year), str(month))


class NewsmaxExtractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div#artPgLeftWrapper"]
        self.img_p_selector = ["#artPgHdLnWrapper"]
        self.img_selector = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h1.article"]
        self.head_img_select = []

    def extract_html(self, url):
        """
        Extract the image and text content from and HTML:
        Inputs:
            - html(str): Full html of an artcile url
            - article_selector(str): css selector for article container
            - head_img_div(list)- css selector for parent div of headline image
            - head_img_select(list)- css selector for images
            - img_p_selector(list): css selector for the parent elements of
            images in article
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

        html = page_grab(url)

        # Obtain article body
        for selector in self.article_body:
            if len(html.cssselect(selector)[0]) > 0:
                article_body = html.cssselect(selector)[0]
                break

        # Obtain images
        imgs += self.extract_imgs(article_body, self.img_p_selector, self.img_selector)
        imgs += self.extract_social_media_image(html)
        imgs += self.extract_video_thumbnails(html)

        # Obtain article and title text
        art_text = self.extract_text(article_body, self.p_selector)

        for t in self.t_selector:
            if html.cssselect(t)[0].text is not None:
                t_text = html.cssselect(t)[0].text
                break
        return imgs, art_text, t_text

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

        img_container = html.cssselect(img_p_selector[0])

        # Obtain img info and captions which in the Daily both live inside the
        # same parent element (img_container)
        for container in img_container:
            # Inside the image container when grabbing the caption there are two elements
            # The first has empty text while the second one contains the caption
            caption = container.cssselect("div.artCaptionContainer")[1].text
            for j in img_selector:
                photos = container.cssselect(j)
                # Videos live inside the same container as video so need to do
                # additional check to avoid errors
                if photos:
                    for i in photos:
                        img_item = Image(
                            url=i.get("src") or "",
                            image_type=ImageType("main"),
                            caption=caption or "",
                            alt_text=i.get("alt") or "",
                        )
                    imgs.append(img_item)

        return imgs

    def extract_video_thumbnails(self, html):
        caption = html.cssselect("div.artCaptionContainer")[1].text
        video_element = html.cssselect("meta[itemprop=thumbnailUrl]")
        if video_element:
            img_item = Image(
                url=video_element[0].get("content"),
                alt_text="",
                caption=caption or "",
                image_type=ImageType("video_thumbnail"),
            )
            return [img_item]
        else:
            return []
