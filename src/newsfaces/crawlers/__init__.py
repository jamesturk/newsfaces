from .ap import APArchive
from .bbc import BBCArchive, BBC_Latest
from .breitbart import BreitbartArchive
from .cnn import CnnArchive
from .daily import DailyCrawler
from .fox import FoxArchive, Fox_API, Fox_Extractor
from .hill import TheHillArchive, Hill_Extractor
from .nbc import NBCArchive
from .newsmax import NewsmaxCrawler
from .npr import NprCrawler
from .nyt import NYTCrawler
from .politico import Politico, Politico_Extractor
from .wapo import WashingtonPostArchive, WashingtonPost_API
from .washington_times import WashingtonTimesArchive, WashingtonTimes_Extractor

__all__ = [
    "APArchive",
    "BBCArchive",
    "BBC_Latest",
    "BreitbartArchive",
    "CnnArchive",
    "DailyCrawler",
    "FoxArchive",
    "Fox_API",
    "Fox_Extractor",
    "TheHillArchive",
    "Hill_Extractor",
    "NBCArchive",
    "NewsmaxCrawler",
    "NprCrawler",
    "NYTCrawler",
    "Politico",
    "Politico_Extractor",
    "WashingtonPostArchive",
    "WashingtonPost_API",
    "WashingtonTimes_Extractor",
    "WashingtonTimesArchive",
]
