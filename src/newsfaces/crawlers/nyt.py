from ..crawler import Crawler, START_DATE, END_DATE
from ..utils import make_link_absolute
from ..models import Article, Image, ImageType
import json
import requests
import time
import re

nyt_api_key = ""
POLITICS_SECTION = '"politics"'
SLEEP_TIME = 12


class NYTCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?"

    def make_request(
        self,
        news_desk=POLITICS_SECTION,
        begin_date=START_DATE,
        end_date=END_DATE,
        page="0",
    ):
        """
        Make a GET request to the NYT Article Search API with a request delay of 6
            seconds to avoid reaching request limit of 60 requests per minute.

        Inputs:
            tags (lst): list of tags (strings) to look for. The tags to filter for
                are looked in the body, headline and byline of the articles.
            filters (lst): list of filters where to look tags. They can be "headline",
                "lead_paragraph" and/or "body"
            begin_date (str): 8 digits (YYYYMMDD) string that specify the begin date
                or from when to start looking for articles.
            end_date (str): 8 digits (YYYYMMDD) string that specify the end date or
                until when to stop looking for articles.
            page (str): number of page string that states where to look for articles.

        Return (Response): API request response with specified query parameters
        """

        begin_date = begin_date.strftime("%Y%m%d")
        end_date = end_date.strftime("%Y%m%d")
        fq = "news_desk:(" + news_desk + ")"

        parameters = {
            "fq": fq,
            "begin_date": begin_date,
            "end_date": end_date,
            "sort": "oldest",
            "page": page,
            "api-key": nyt_api_key,
        }

        resp = requests.get(self.start_url, params=parameters)
        resp_json = json.loads(resp.text)

        return resp_json

    def crawl(
        self,
        news_desk=POLITICS_SECTION,
        begin_date=START_DATE,
        end_date=END_DATE,
    ):
        """
        Crawl NYT to obtain all the information
        """

        page_responses = []

        resp = self.make_request(news_desk, begin_date, end_date)
        page_responses.append(resp)
        # Get number of articles that match our query search parameters
        hits = resp["response"]["meta"]["hits"]

        # Get maximum number of pages we can query
        max_pages = int(hits / 10)

        for page_n in range(1, max_pages + 1):
            # Limit of 5 requests per minute
            print("Obtaining results for page", page_n, "/", max_pages)
            time.sleep(SLEEP_TIME)
            resp = self.make_request(news_desk, begin_date, end_date, page=str(page_n))
            status = resp.get("status")
            page_responses.append(resp)

            if status != "OK":
                break

        return page_responses


class NYTExtractor:
    def __init__(self):
        self.prefix = "https://www.nytimes.com/images/"
        self.pattern = "^images\/\d{4}\/\d{2}\/\d{2}\/[a-zA-Z]+\/([^\/]+)\/"

    def clean_imgs(self, nyt_art):
        """
        Create images list deduplicating images
        """
        imgs_list = []
        img_prefixes = set()
        multimedia = nyt_art["multimedia"]
        for item in multimedia:
            match = re.match(self.pattern, item["url"])
            if match:
                img_prefix = match.group()
            else:
                img_prefix = None
            partial_url = "/" + item["url"]
            item_url = make_link_absolute(partial_url, self.prefix)
            # The NYT API response include multiple versions of the same image
            # We are keeping only the first observation to avoid duplication
            if img_prefix in img_prefixes:
                continue
            else:
                img_prefixes.add(img_prefix)
                img_item = Image(
                    url=item_url,
                    caption=item["caption"] or "",
                    image_type=ImageType("main"),
                )
                imgs_list.append(img_item)
        return imgs_list

    def scrape(self, nyt_art):
        """
        Convert article in NYT response into Article object
        """
        t_text = nyt_art["headline"]["main"]
        lead_paragraph = nyt_art["lead_paragraph"]
        imgs_list = self.clean_imgs(nyt_art)
        return Article(title=t_text, article_text=lead_paragraph, images=imgs_list)
