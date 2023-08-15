from databeakers import Pipeline
from databeakers.http import HttpResponse, HttpRequest
from .models import ArticleURL, Article
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


def article_seed_wrapper(crawl_func, source):
    """
    Convert a function that returns a list of article URLs (strings)
    into a function that returns an iterable that contains ArticleURL
    objects tagged with the source.
    """

    def new_func():
        for url in crawl_func():
            yield ArticleURL(url=url, source=source)

    return new_func


pipeline = Pipeline("newsfaces", "newsfaces.db")


SOURCE_MAPPING = {
    "ap": (AP(), None),
    "bbc_archive": (BBC(), None),
    "bbc_latest": (BBC_Latest(), None),
    "breitbart": (BreitbartCrawler(), None),
    "cnn": (CnnCrawler(), None),
    "daily": (DailyCrawler(), None),
    "fox": (Fox(), None),
    "fox_api": (Fox_API(), None),
    "hill": (TheHill(), None),
    "nbc": (NBC(), None),
    "newsmax": (NewsmaxCrawler(2021), None),
    "npr": (NprCrawler(), None),
    "politico": (Politico(), None),
    "wapo": (WashingtonPost(), None),
    "wapo_api": (WashingtonPost_API(), None),
    "washtimes": (WashingtonTimes(), None),
}

# For now, we're going to construct parallel pipelines for each source.
# Each will go from url -> response -> article
for source, classes in SOURCE_MAPPING.items():
    pipeline.add_beaker(f"url_{source}", ArticleURL)
    pipeline.add_beaker(f"response_{source}", HttpResponse)
    pipeline.add_beaker(f"article_{source}", Article)
    (crawler, extractor) = classes
    pipeline.add_seed(
        source, f"url_{source}", article_seed_wrapper(crawler.crawl, source)
    ),
    pipeline.add_transform(
        f"url_{source}",
        f"response_{source}",
        HttpRequest,
    )
    # TODO: uncomment once extractors are in place
    # pipeline.add_transform(f"response_{source}", f"article_{source}", extractor)
