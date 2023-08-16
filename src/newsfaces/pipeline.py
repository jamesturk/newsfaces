import itertools
from databeakers.pipeline import Pipeline
from databeakers.http import HttpResponse, HttpRequest
from databeakers.transforms import RateLimit, Conditional
import httpx
from .models import URL, Article
from .pipeline_helpers import (
    article_seed_wrapper,
    make_comparator,
    make_extractor,
)
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

"""
This file defines the pipeline for the newsfaces project.

This is the pipeline object, it will be imported by `bkr` when you run it.
(Typically you don't put code at the top level of the file, but this is a
 relatively common exception. Sometimes called a "plugin" pattern, 
 the main bkr code finds this file and imports the pipeline object.)

Pipeline takes a name and a database file name.
"""
pipeline = Pipeline("newsfaces", "newsfaces.db")


"""
Next we just create a convinience mapping between short names & their respective classes.

An alternative to this would be to have the classes be named very rigidly (e.g. ap.Crawler, ap.Extractor) 
so they could be derived automatically.  

**Note:** To enable extraction, change the second member of the tuple to the appropriate extractor class.
"""
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

"""
Now we can build the pipeline programmatically.

It is important to understand, the below code is really just configuration.

* add_beaker(name, datatype) - defines a new type of data that can be passed between transforms
* add_seed(name, dest_beaker, function) - defines a function that will populate dest_beaker
* add_transform(from_beaker, to_beaker, function) - define a transformation from one type to another

We run this code in a loop since each source has the same basic structure.
"""
for source, classes in WAYBACK_SOURCE_MAPPING.items():
    (crawler, extractor) = classes

    """
    Wayback crawlers start with archive_url, these are archive.org URLs to be crawled.

    We define the beaker, and add a seed mapping source_name -> crawler.get_wayback_urls
    """
    pipeline.add_beaker("archive_url", URL)
    pipeline.add_seed(
        source,
        "archive_url",
        crawler.get_wayback_urls,
    )

    """
    Next we add a transformation from URL -> WebResponse with some error handling.
    """
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

    """
    Finally we add a transformation from archive_response to {source}_url.
      
    {source}_url would now be populated with the URLs of the articles on the page.

    This transform is a bit more complicated, because we want to split the archive_response
    beaker (which is all sources mixed up) into different functions per-source.

    Right now this code is IMO too complex, but it works. 
    Once the interface is more stable, I've left a note to refactor this piece.

    TODO: make_comparator could become Conditional(field="source", value=source) with a bit of work
    """
    pipeline.add_beaker(f"{source}_url", URL)
    pipeline.add_transform(
        f"archive_response",
        f"{source}_url",
        Conditional(
            make_extractor("archive_response", crawler.get_article_urls),
            make_comparator(source),
        ),
        whole_record=True,
    )

"""
The setup for a non-wayback crawler is much more simple.

We still want to wind up with a {source}_url beaker,  but we just use
crawler.crawl directly, since it returns a iterable of URLs.
"""
for source, classes in SOURCE_MAPPING.items():
    (crawler, extractor) = classes
    pipeline.add_beaker(f"{source}_url", URL)
    pipeline.add_seed(
        source, f"{source}_url", article_seed_wrapper(crawler.crawl, source)
    )

"""
We continue defining the pipeline, from this point forward it is the same for both.

{source_url} becomes {source_response} through HttpRequest again, aggregating errors/timeouts into the same beakers.

{source_response} then needs to become {article}, which is done by the extractor.
"""
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
        pipeline.add_transform(f"{source}_response", f"article", extractor)
