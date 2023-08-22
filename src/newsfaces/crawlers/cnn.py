import re
import lxml.html
import requests
import datetime
import pytz
from databeakers.http import HttpResponse
from ..crawler import WaybackCrawler
from ..utils import make_link_absolute
from ..models import URL
from typing import Generator

# The results for https://cnn.com/politics have different types of answers
# depending on the date so we need to create additional datetime objects to deal
# with different periods
# I) 2015 - Oct 18 2016: Archive works ok, no Java Script
# II) Oct 18 2016 - Jan 30 2017: Internet Archive result does not work. There
# is a CNN loading logo but no urls appear
# III) Jan 31st 2017 - Dec 13 2022: Archive works ok, uses Java Script
# IV) Dec 13 2022 - present: Archive works ok, no Java Script

# Date of first archived with JS
JS_START_DATE = datetime.datetime(2017, 1, 31, 6, 39, 53, tzinfo=pytz.timezone("utc"))
# Date of first archived without JS
JS_END_DATE = datetime.datetime(2022, 12, 13, 0, 33, 15, tzinfo=pytz.timezone("utc"))
# Date of first archived with no results
STOP_WORKING_DATE = datetime.datetime(
    2016, 10, 18, 17, 41, 32, tzinfo=pytz.timezone("utc")
)


class CnnArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("cnn")
        self.start_url = "https://www.cnn.com/politics/"
        self.selector = ["div.container__item", "h3.cd__headline"]
        self.session_js = requests.Session()

    def get_archive_urls_js(self, time_str):
        urls = []
        json_url = (
            f"https://web.archive.org/web/{time_str}/"
            "https://www.cnn.com/data/ocs/section/politics/index.html:"
            "politics-zone-1/views/zones/common/zone-manager.izl"
        )
        resp = self.session_js.get(json_url)
        resp_json = resp.json()
        html = lxml.html.fromstring(resp_json["html"])

        article_elements = html.cssselect("h3.cd__headline")
        article_link = article_elements[0].cssselect("a")[0].get("href")
        article_link

        for article in article_elements:
            rel_link = article.cssselect("a")[0].get("href")
            absolute_link = make_link_absolute(rel_link, "https://www.cnn.com")

            urls.append(URL(url=absolute_link, source=self.source_name))

        return urls

    def get_article_urls(self, response: HttpResponse) -> Generator[URL, None, None]:
        time_str = re.findall(r"(\d{14})", response.url)[0]
        time_stamp = datetime.datetime.strptime(time_str, "%Y%m%d%H%M%S").astimezone(
            pytz.timezone("utc")
        )
        if JS_START_DATE < time_stamp < JS_END_DATE:
            yield from self.get_archive_urls_js(time_str)
        else:
            yield from super().get_article_urls(response)
