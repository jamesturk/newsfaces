from beakers import Pipeline
from beakers.http import HttpResponse, HttpRequest
from .models import ArticleURL
from .crawlers import (
    AP,
    BBC,
    BBC_Latest,
    BreitbartCrawler,
    CnnCrawler,
    DailyCrawler,
    Fox,
    # we do need both fox scrapers
    Fox_API,
    TheHill,
    NBC,
    NewsmaxCrawler,
    NprCrawler,
    Politico,
    WashingtonPost,
    WashingtonPost_API,
    WashingtonTimes,
)

pipeline = Pipeline("newsfaces", "newsfaces.db")

pipeline.add_beaker("article", ArticleURL)
pipeline.add_beaker("response", HttpResponse)
pipeline.add_transform(
    "article",
    "response",
    HttpRequest,
)

pipeline.add_seed("ap", "article", AP())
