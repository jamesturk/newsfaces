from databeakers.pipeline import Pipeline, ErrorType
from databeakers.http import HttpResponse, HttpRequest
from databeakers.transforms import RateLimit
import httpx
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


WAYBACK_SOURCE_MAPPING = {
    "ap": (AP(), None),
    "bbc_archive": (BBC(), None),
    "cnn": (CnnCrawler(), None),
    "fox": (Fox(), None),
    "nbc": (NBC(), None),
    "wapo": (WashingtonPost(), None),
    "breitbart": (BreitbartCrawler(), None),
    "hill": (TheHill(), None),
    "washtimes": (WashingtonTimes(), None),
}

SOURCE_MAPPING = {
    "bbc_latest": (BBC_Latest(), None),
    "daily": (DailyCrawler(), None),
    "fox_api": (Fox_API(), None),
    "newsmax": (NewsmaxCrawler(2021), None),
    "npr": (NprCrawler(), None),
    "politico": (Politico(), None),
    "wapo_api": (WashingtonPost_API(), None),
}


for source, classes in WAYBACK_SOURCE_MAPPING.items():
    (crawler, extractor) = classes

    pipeline.add_beaker("archive_url", ArticleURL)
    pipeline.add_seed(
        source,
        "archive_url",
        crawler.get_wayback_urls,
    )
    pipeline.add_beaker("archive_response", HttpResponse)
    pipeline.add_transform(
        "archive_url",
        "archive_response",
        RateLimit(HttpRequest(), 1),
        error_map={
            (httpx.ReadTimeout,): "archive_timeouts",
            (httpx.RequestError,): "archive_errors",
        },
    )

    # TODO: populate url_{source} with the archive urls

# the non-wayback crawlers are url -> response -> article
for source, classes in SOURCE_MAPPING.items():
    pipeline.add_beaker(f"url_{source}", ArticleURL)
    pipeline.add_seed(
        source, f"url_{source}", article_seed_wrapper(crawler.crawl, source)
    ),
    pipeline.add_transform(
        f"url_{source}",
        f"response_{source}",
        HttpRequest(),
    )
    # TODO: uncomment once extractors are in place
    # pipeline.add_beaker(f"article_{source}", Article)
    # pipeline.add_transform(f"response_{source}", f"article_{source}", extractor)
