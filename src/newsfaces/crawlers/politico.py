from newsfaces.extract_html import Extractor
from newsfaces.utils import make_link_absolute, page_grab
from newsfaces.crawler import Crawler
from newsfaces.models import Image, Article, ImageType, URL


class Politico(Crawler):
    def __init__(self):
        super().__init__()
        self.source = "politico"

    def crawl(self):
        for page in range(1, 3400):
            yield from self.get_urls(f"https://www.politico.com/politics/{page}")

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
        container = response.cssselect("div.summary")

        for j in container:
            atr = j.cssselect("a")
            if atr and len(atr) > 0:
                href = atr[0].get("href")
                yield URL(
                    url=make_link_absolute(href, "https://www.politico.com"),
                    source=self.source,
                )


class Politico_Extractor(Extractor):
    def __init__(self):
        super().__init__()
        self.article_body = ["div.story-text", "div.super-inner"]
        self.img_p_selector = [
            "section.media-item.media-item--story.media-item--story-lead"
        ]
        self.img_selector = ["img"]
        self.head_img_div = []
        self.video = ["div.media-item__video"]
        self.head_img_select = []
        self.p_selector = ["p.story-text__paragraph"]
        self.t_selector = ["h2.headline"]

    def get_video_imgs(self, html):
        videos = []
        imgs = []

        for i in self.video:
            videos += html.cssselect(i)
            item = []
            cap_elements = []
            for v in videos:
                item += v.cssselect("video")
                cap_elements += v.xpath('//div[contains(@class, "vjs-dock-text")]')

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



