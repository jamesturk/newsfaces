import itertools
from databeakers.pipeline import Pipeline
from databeakers.http import HttpResponse, HttpRequest
from databeakers.transforms import RateLimit, Conditional
from databeakers._record import Record
from pydantic import BaseModel
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
    Fox_API,
    TheHill,
    NBC,
    NewsmaxCrawler,
    NprCrawler,
    NYTCrawler,
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
    # "ap": (AP(), None),
    "bbc_archive": (BBC(), None),
    "breitbart": (BreitbartCrawler(), None),
    "cnn": (CnnCrawler(), None),
    "fox": (Fox(), None),
    "hill": (TheHill(), None),
    "nbc": (NBC(), None),
    "wapo": (WashingtonPost(), None),
    "washtimes": (WashingtonTimes(), None),
}

SOURCE_MAPPING = {
    "bbc_latest": (BBC_Latest(), None),
    "daily": (DailyCrawler(), None),
    "fox_api": (Fox_API(), None),
    "newsmax": (NewsmaxCrawler(2021), None),
    "npr": (NprCrawler(), None),
    "nyt": (NYTCrawler(), None),
    "politico": (Politico(), None),
    "wapo_api": (WashingtonPost_API(), None),
}


def make_comparator(source: str):
    def fn(record: Record) -> bool:
        return record["archive_url"].source == source

    fn.__name__ = f"is_{source}"

    return fn


def make_extractor(beaker_name: str, fn):
    def new_fn(record: Record) -> BaseModel:
        yield from fn(record[beaker_name])

    new_fn.__name__ = fn.__name__
    return new_fn


# wayback crawlers all process through the archive_url beaker
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

    pipeline.add_beaker(f"{source}_url", ArticleURL)
    # TODO: make_comparator could become Conditional(field="source", value=source) with a bit of work
    pipeline.add_transform(
        f"archive_response",
        f"{source}_url",
        Conditional(
            make_extractor("archive_response", crawler.get_article_urls),
            make_comparator(source),
        ),
        whole_record=True,
    )

# the non-wayback crawlers seed right into URL
for source, classes in SOURCE_MAPPING.items():
    (crawler, extractor) = classes
    pipeline.add_beaker(f"{source}_url", ArticleURL)
    pipeline.add_seed(
        source, f"{source}_url", article_seed_wrapper(crawler.crawl, source)
    )

# this part is the same for both
# url -> response -> article
for source, classes in itertools.chain(
    WAYBACK_SOURCE_MAPPING.items(), SOURCE_MAPPING.items()
):
    (crawler, extractor) = classes
    pipeline.add_transform(
        f"{source}_url",
        f"{source}_response",
        HttpRequest(),
        error_map={
            (httpx.ReadTimeout,): "timeouts",
            (httpx.RequestError,): "errors",
        },
    )
    if extractor:
        pipeline.add_transform(f"{source}_response", f"{source}_article", extractor)
