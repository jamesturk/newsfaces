from databeakers._record import Record
from pydantic import BaseModel

"""
These are not part of the
pipeline but are used to make it easier to define the pipeline without duplicating
code.  These should probably be moved into the databeakers library at some point
but were added here for expediency.

(These use some advanced Python metaprogramming features, and you do not need to
understand them to work with the pipeline.)
"""


def article_seed_wrapper(crawl_func, source):
    """
    Convert a function that returns a list of article URLs (strings)
    into a function that returns an iterable that contains URL
    objects tagged with the source.
    """

    def new_func():
        for url in crawl_func():
            yield URL(url=url, source=source)

    return new_func


def make_comparator(source: str):
    """
    Build a comparator function to filter on source.
    """

    def fn(record: Record) -> bool:
        return record["archive_url"].source == source

    fn.__name__ = f"is_{source}"

    return fn


def make_extractor(beaker_name: str, fn):
    """
    Unwrap a Record.
    """

    def new_fn(record: Record) -> BaseModel:
        yield from fn(record[beaker_name])

    new_fn.__name__ = fn.__name__
    return new_fn
