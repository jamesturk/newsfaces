from .crawler import WaybackCrawler, START_DATE, END_DATE, DELTA_HRS
from wayback import memento_url_data
from ..utils import make_link_absolute
import lxml.html
import requests
import datetime
import pytz

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

    def get_archive_urls_njs(self, url, selectors):
        return super().get_archive_urls(url, selectors)

    def get_archive_urls_js(self, wayback_record):
        urls = []
        time_stamp = wayback_record.timestamp.strftime("%Y%m%d%H%M%S")
        json_url = """https://web.archive.org/web/{}/https://www.cnn.com/
        data/ocs/section/politics/index.html:politics-zone-1/
        views/zones/common/zone-manager.izl""".format(
            time_stamp
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

            urls.append(absolute_link)

        return urls

    def crawl(self, start_date=START_DATE, end_date=END_DATE, delta_hrs=DELTA_HRS):
        """
        Crawl to obtain all the urls of articles contained in start_url in the different
        stored versions in the internet archive between two dates.

        Inputs:
        - start_date(datetime object): Earliest day for which to look for results
        - end_date(datetime object): Latest day for which to look for results
        -delta_hrs (int): Threshold of minimum number of hours between the
                        timestamp of consecutive internet archive results
                        for which to look for article urls.
        Return:
        - post_date_articles(set): Set of urls obtained from the crawling process
        """
        post_date_articles = set()

        # Get first result
        current_date = start_date
        results = self.client.search(
            self.start_url, match_type="exact", from_date=current_date
        )
        record = next(results)

        # Crawl internet archive in gaps of at least delta_hrs
        while current_date < end_date:
            # Check if timestamp is a time where specific function for a
            # cnn archived webpage that uses java script
            if JS_START_DATE <= current_date <= JS_END_DATE:
                articles = self.get_archive_urls_js(record)
            else:
                waybackurl = record.view_url
                articles = self.get_archive_urls_njs(waybackurl, self.selector)
                articles = [
                    memento_url_data(item)[0]
                    if ("/web/" in item or "web.archive.org" in item)
                    else item
                    for item in articles
                ]

            post_date_articles.update(articles)

            # Continue only if it's possible to visit another result
            try:
                next_result = next(results)
            except StopIteration:
                break
            next_time = next_result.timestamp

            # Check time conditions for CNN
            # Avoid visiting archived cnn pages that not work
            if STOP_WORKING_DATE <= next_time <= JS_START_DATE:
                current_date = JS_START_DATE
                results = self.client.search(
                    self.start_url, match_type="exact", from_date=current_date
                )
                record = next(results)
            # If gap between fetched and next result is less than delta_hrs,
            # search the archive for the first results in at least delta_hrs
            elif next_time - current_date < datetime.timedelta(hours=delta_hrs):
                current_date += datetime.timedelta(hours=delta_hrs)
                results = self.client.search(
                    self.start_url, match_type="exact", from_date=current_date
                )
                record = next(results)
            else:
                current_date = next_time
                record = next_result

        return post_date_articles
