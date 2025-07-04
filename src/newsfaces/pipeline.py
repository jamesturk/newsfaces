import itertools
from databeakers.pipeline import Pipeline
from databeakers.edges import FieldSplitter, Transform
from databeakers.http import HttpEdge
from databeakers.decorators import rate_limit
from lxml.etree import ParserError
from .models import URL, Article
from .pipeline_helpers import make_extractor
from .crawlers import (
    APArchive,
    AP_Extractor,
    BBCArchive,
    BBC_Latest,
    BBC_Extractor,
    BreitbartArchive,
    CnnArchive,
    DailyCrawler,
    FoxArchive,
    Fox_API,
    TheHillArchive,
    NBCArchive,
    NewsmaxCrawler,
    NprCrawler,
    NYTCrawler,
    Politico,
    WashingtonPostArchive,
    WashingtonPost_API,
    WashingtonTimesArchive,
    # Extractors
    Politico_Extractor,
    Hill_Extractor,
    Fox_Extractor,
    NBC_Extractor,
    WashingtonTimes_Extractor,
)
from .extract_html import MissingBodyError

from .crawlers.npr import NPRExtractor
from .crawlers.daily import DailyExtractor
from .crawlers.breitbart import BreitbartExtractor
from .crawlers.newsmax import NewsmaxExtractor
from .crawlers.cnn import CNNExtractor

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
Next we just create a convenience mapping between short names & their respective classes.

An alternative to this would be to have the classes be named very rigidly (e.g. ap.Crawler,
 ap.Extractor) so they could be derived automatically.  

**Note:** To enable extraction, change the second member of the tuple to the appropriate
 extractor class.
"""
WAYBACK_SOURCE_MAPPING = {
    "ap": (APArchive(), AP_Extractor()),
    "bbc": (BBCArchive(), BBC_Extractor()),
    "breitbart": (BreitbartArchive(), BreitbartExtractor()),
    "cnn": (CnnArchive(), CNNExtractor()),
    "fox": (FoxArchive(), Fox_Extractor()),
    "hill": (TheHillArchive(), Hill_Extractor()),
    "nbc": (NBCArchive(), NBC_Extractor()),
    "wapo": (WashingtonPostArchive(), None),
    "washtimes": (WashingtonTimesArchive(), WashingtonTimes_Extractor()),
}

SOURCE_MAPPING = {
    "bbc_latest": (BBC_Latest(), None),
    "daily": (DailyCrawler(), DailyExtractor()),
    "fox_api": (Fox_API(), Fox_Extractor()),
    "newsmax": (NewsmaxCrawler(), NewsmaxExtractor()),
    "npr": (NprCrawler(), NPRExtractor()),
    "nyt": (NYTCrawler(), None),
    "politico": (Politico(), Politico_Extractor()),
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

"""
First we add the archive_url -> response transformation.
"""
pipeline.add_beaker("archive_url", URL)
pipeline.add_out_transform(
    "archive_url",
    HttpEdge(
        "archive_response",
        timeout_beaker="archive_timeouts",
        error_beaker="archive_errors",
        bad_response_beaker="archive_bad_response",
    ),
).decorate(rate_limit, 1)

splitter_map = {}
for source, classes in WAYBACK_SOURCE_MAPPING.items():
    (crawler, extractor) = classes

    """
    Wayback crawlers start with archive_urls, these are archive.org URLs to be crawled.
    """
    pipeline.register_seed(
        crawler.get_wayback_urls,
        "archive_url",
        seed_name=source,
    )

    """
    Next we add the {source}_url beaker & create a transform that calls the appropriate
    get_article_urls on the response.

    We keep these transforms in a dict so we can use them later.
    """
    pipeline.add_beaker(f"{source}_url", URL)
    splitter_map[source] = Transform(
        to_beaker=f"{source}_url",
        func=make_extractor("archive_response", crawler.get_article_urls),
        name=f"{source}.get_article_urls",
        allow_filter=True,
        # TODO: right now some get_article_urls are returning empty lists
        # you can see this by looking at the logs where you see something like
        # transform (generator) with yield of 0 items
        # if you set allow_filter=False, these will raise an exception instead
        # of being ignored
    )

pipeline.add_splitter(
    "archive_response",
    FieldSplitter(
        "source",
        splitter_map,
        beaker_name="archive_url",
        whole_record=True,
    ),
)

"""
The setup for a non-wayback crawler is much more simple.

We still want to wind up with a {source}_url beaker,  but we just use
crawler.crawl directly, since it returns a iterable of URLs.
"""
for source, classes in SOURCE_MAPPING.items():
    (crawler, extractor) = classes
    pipeline.add_beaker(f"{source}_url", URL)
    pipeline.register_seed(crawler.crawl, f"{source}_url", seed_name=source)

"""
We continue defining the pipeline, from this point forward it is the same for both.

{source_url} becomes {source_response} through HttpRequest again, aggregating 
errors/timeouts into the same beakers.

{source_response} then needs to become {article}, which is done by the extractor.
"""
pipeline.add_beaker("article", Article)
for source, classes in itertools.chain(
    WAYBACK_SOURCE_MAPPING.items(), SOURCE_MAPPING.items()
):
    (crawler, extractor) = classes
    if source == "hill":
        headers = {
            "user-agent": (
                "Mozilla/5.0 (Linux; Android 6.0; Nexus 5 Build/MRA58N) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/92.0.4515.107 Mobile Safari/537.36"
            )
        }
    else:
        headers = None
    edge = pipeline.add_out_transform(
        f"{source}_url",
        HttpEdge(
            f"{source}_response",
            timeout_beaker="timeouts",
            error_beaker="errors",
            bad_response_beaker=f"{source}_bad_response",
            headers=headers,
        ),
    )
    if source == "newsmax":
        edge.decorate(rate_limit, 0.5)

    if extractor:
        pipeline.add_transform(
            f"{source}_response",
            "article",
            extractor.scrape,
            error_map={
                (MissingBodyError, ParserError): "selector_errors",
            },
        )
