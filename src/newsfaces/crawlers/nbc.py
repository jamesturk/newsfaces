from ..crawler import WaybackCrawler
from ..models import URL
import re


url = "https://www.nbcnews.com/politics/"


class NBCArchive(WaybackCrawler):
    def __init__(self):
        super().__init__("nbc")
        self.start_url = "https://www.nbcnews.com/politics"
        self.selector = []
        self.source = "nbc"

    def get_article_urls(self, response):
        # Retrieve the raw HTML content
        html = response.response_body
        # Define the pattern and delimiter
        pattern = f'href="{url}'

        delimiter = '"'

        # Find all matches of the pattern in the HTML content
        matches = re.finditer(pattern, html)
        # Process each match
        for match in matches:
            start_index = match.end()
            end_index = html.find(delimiter, start_index)
            if end_index != -1:
                content = html[start_index:end_index]
                if re.search(r".*/.*-.*-.*-", content):
                    fullurl = url + content
                    yield URL(url=fullurl, source=self.source)
