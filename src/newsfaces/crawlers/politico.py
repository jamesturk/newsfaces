# Util Functions
from newsfaces.extract_html import Extractor
from newsfaces.utils import make_link_absolute, page_grab
from newsfaces.crawler import Crawler
from newsfaces.models import Image, Article, ImageType


class Politico(Crawler):
    def __init__(self):
        super().__init__()

    def crawl(self):
        """
        Implement crawl here to override behavior
        """
        return self.politico_get_urls()

    def get_urls(self, url):
        """
        This function takes a URLs and returns lists of URLs
        for containing each article on that page.

        Parameters:
            * url:  a URL to a page of articles

        Returns:
            A list of article URLs on that page.
        """
        response = self.make_request(url)
        urls = []
        container = response.cssselect("div.summary")

        for j in container:
            atr = j.cssselect("a")
            if atr and len(atr) > 0:
                href = atr[0].get("href")
                urls.append(make_link_absolute(href, "https://www.politico.com"))
        return urls

    def recurse_politico(self, url, breakpoint, urls=[]):
        """
        Runs get_url's function on all possible article landing pages
        until a specific page (breakpoint). Returns a list of article
        urls across pages
        """
        scraped_urls = self.get_urls(url)
        urls += scraped_urls
        begin = url.find("politics/") + 9
        pagenumber = int(url[begin : len(url)])
        if pagenumber < breakpoint:
            newlink = url[: -len(str(pagenumber))] + str(pagenumber + 1)
            self.recurse_politico(newlink, breakpoint, urls)
        return urls

    def politico_get_urls(self):
        urllist = self.recurse_politico("https://www.politico.com/politics/1", 1700)
        urllist2 = self.recurse_politico("https://www.politico.com/politics/1700", 3400)
        pooled = set(urllist + urllist2)
        return pooled


class Politico_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div.story-text"]
        self.img_p_selector = [
            "section.media-item.media-item--story.media-item--story-lead"
        ]
        self.img_selector = ["img"]
        self.head_img_div = [
            "section.media-item.media-item--story.media-item--story-lead"
        ]
        self.video = ["div.media-item__video"]
        self.head_img_select = ["img"]
        self.p_selector = ["p"]
        self.t_selector = ["h2.headline"]

    def scrape(self, url):
        """
        Extract html and from
        """
        html = page_grab(url)
        imgs, art_text, t_text = self.extract_html(html)
        imgs += self.extract_video_imgs(html)
        article = Article(title=t_text or "", article_text=art_text or "", images=imgs)
        return article

    def extract_video_imgs(self, html):
        videos = []
        imgs = []
        print(html)
        for i in self.video:
            videos += html.cssselect(i)
            for v in videos:
                item = v.cssselect("video")
                v.xpath('//div[contains(@class, "vjs-dock-text")]')

            cap_elements = v.xpath('//div[contains(@class, "vjs-dock-text")]')

            # Extract captions from cap_elements
            captions = [element.text_content() for element in cap_elements]

            for i, video in enumerate(item):
                img_item = Image(
                    url=video.get("poster") or "",
                    image_type=ImageType("video_thumbnail"),
                    caption=captions[i] if i < len(captions) else "",
                    alt_text="",
                )
                imgs.append(img_item)

        return imgs

    def extract_head_img(self, html, img_p_selector, img_selector):
        return []
