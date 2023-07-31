from .crawler import Crawler, START_DATE, END_DATE
from ..utils import make_link_absolute
import json
import requests
import time

POLITICS_SECTION = "politics"
QUERY_LIST = ["Donald Trump", "Joe Biden"] #Add default names of politicians to look for 
#if we go with search approach
FILTER_LIST = ["headline", "lead_paragraph"]
nyt_api_key = "AUtPPNuICzon3X9uEaX2k4Dgs0YGBA25" ##Move to config file


class NYTCrawler(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://api.nytimes.com/svc/search/v2/articlesearch.json?"

               
    def create_url(self,tags=None,news_desk=POLITICS_SECTION, section = "Washington", filters=FILTER_LIST, begin_date=START_DATE,
    end_date=END_DATE, page="0"):
        """
        Create request url for API based on query search parameters passed to the
            function.
        
        Inputs:
            tags (lst): list of tags (strings) to look for. The tags to filter for
                are looked in the filters defined in the "filters" parameter.
            filters (lst): list of filters where to look tags. They can be "headline",
                "lead_paragraph" and/or "body"
            begin_date (str): 8 digits (YYYYMMDD) string that specify the begin date
                or from when to start looking for articles.
            end_date (str): 8 digits (YYYYMMDD) string that specify the end date or
                until when to stop looking for articles.
            page (str): number of page string that states where to look for articles.

        Return (str): URL string with query to send request to NYT Article Search 
            API
        """
        #Convert datetime object to str to pass it into API
        begin_date = begin_date.strftime("%Y%m%d")
        end_date = end_date.strftime("%Y%m%d")

        tags_copy = tags[:]
        filters_copy = filters[:]

        #Create URL
        if tags:
            tags_copy = tags[:]
            filters_copy = filters[:]
            for i,tag in enumerate(tags_copy):
                tags_copy[i] = "\"" + tag + "\""
            for i, fil in enumerate(filters_copy):
                filters_copy[i] = fil + ":(" + " OR ".join(tags_copy) + ")"
            fq = "fq=" + " OR ".join(filters_copy) + " AND news_desk=" + news_desk + " AND section=" + section
        else:
            fq = "fq=" + "news_desk=" + news_desk + "AND section=" + section
        url = self.start_url + fq + "&begin_date=" + begin_date + "&end_date=" + end_date +\
                "&page=" + page + "&sort=oldest" + "&api-key=" + nyt_api_key

        return url

    def make_request(self, tags=None,news_desk=POLITICS_SECTION, section = "Washington", filters=FILTER_LIST, begin_date= START_DATE,
    end_date= END_DATE, page="0"):
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

        url = self.create_url(tags, news_desk, section, filters, begin_date, end_date, page)
        resp = requests.get(url)
        resp_json = json.loads(resp.text)

        return resp_json

    def obtains_articles_info(self,resp_json):
        """ 
        Retrieves only the articles information of the JSON response and converts all
        multimedia relative src urls to a full link.
        Inputs: 
        - resp_json (json string): Full json string response from the NYT API call
        Returns:
        - Articles (json string): Obtains the article information of the json response
        """
        articles = resp_json["response"]["docs"]
        for article in articles:
            multimedia = article["multimedia"]
            for item in multimedia:
                url = "/" + item["url"]
                item["url"] = make_link_absolute(url,"https://www.nytimes.com/images/")
        return articles

    def crawl(self,tags=None,news_desk=POLITICS_SECTION, section = "Washington", 
        filters=FILTER_LIST, begin_date=START_DATE, end_date=END_DATE):
        """
        Crawl NYT to obtain all the information
        """

        page_responses = []
        
        resp = self.make_request(tags,news_desk,section,filters,begin_date,end_date)
        articles = self.obtain_articles_info(resp)
        page_responses.append(articles)
        # Get number of articles that match our query search parameters
        hits = resp["response"]["meta"]["hits"]

        # Get maximum number of pages we can query
        max_pages = int(hits / 10)

        for page_n in range(1, max_pages + 1):
            #Limit of 5 requests per minute
            time.sleep(12)
            resp = self.make_request(page = str(page_n))
            status = resp.get("status")
            
            if status == "OK":
                articles = self.obtain_articles_info(resp)
                page_responses.append(articles)
            else:
                break
        return page_responses

        



    
