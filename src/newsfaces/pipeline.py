from databeakers import Pipeline
from databeakers.http import HttpResponse, HttpRequest
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


SOURCE_MAPPING = {
    "ap": (AP(),),
    "bbc_archive": (BBC(),),
    "bbc_latest": (BBC_Latest(),),
    "breitbart": (BreitbartCrawler(),),
    "cnn": (CnnCrawler(),),
    "daily": (DailyCrawler(),),
    "fox": (Fox(),),
    "fox_api": (Fox_API(),),
    "hill": (TheHill(),),
    "nbc": (NBC(),),
    "newsmax": (NewsmaxCrawler(),),
    "npr": (NprCrawler(),),
    "politico": (Politico(),),
    "wapo": (WashingtonPost(),),
    "wapo_api": (WashingtonPost_API(),),
    "washtimes": (WashingtonTimes(),),
}

for source, crawlers in SOURCE_MAPPING.items():
    pipeline.add_beaker(f"article_{source}", ArticleURL)
    pipeline.add_beaker(f"response_{source}", HttpResponse)
    for crawler in crawlers:
        pipeline.add_seed(source, "article", crawler)
    pipeline.add_transform(
        f"article_{source}",
        f"response_{source}",
        HttpRequest,
    )
