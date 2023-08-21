from .ap import APArchive
from .bbc import BBCArchive, BBC_Latest
from .breitbart import BreitbartArchive
from .cnn import CnnArchive
from .daily import DailyCrawler
from .fox import FoxArchive, Fox_API
from .hill import TheHillArchive
from .nbc import NBCArchive
from .newsmax import NewsmaxCrawler
from .npr import NprCrawler
from .nyt import NYTCrawler
from .politico import Politico
from .wapo import WashingtonPostArchive, WashingtonPost_API
from .washington_times import WashingtonTimesArchive

__all__ = [
    "APArchive",
    "BBCArchive",
    "BBC_Latest",
    "BreitbartArchive",
    "CnnArchive",
    "DailyCrawler",
    "FoxArchive",
    "Fox_API",
    "TheHillArchive",
    "NBCArchive",
    "NewsmaxCrawler",
    "NprCrawler",
    "NYTCrawler",
    "Politico",
    "WashingtonPostArchive",
    "WashingtonPost_API",
    "WashingtonTimesArchive",
]
