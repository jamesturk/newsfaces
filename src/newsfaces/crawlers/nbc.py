# Util Functions
from .crawler import WaybackCrawler
import re

url = "https://www.nbcnews.com/politics/"


class NBC(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.nbcnews.com/politics/"
        self.selector = []

    def get_archive_urls(self, url, selectors):
        """
        Implement get_archive_urls here to override behavior
        """
        return self.get_nbc(url, self.session)

    def get_nbc(self, url, session=None):
        response = self.http_get(url, session=None)

        # Retrieve the raw HTML content
        html = response.text
        # Define the pattern and delimiter
        pattern = f'href="{url}'

        delimiter = '"'

        # Find all matches of the pattern in the HTML content
        matches = re.finditer(pattern, html)
        article = set()
        # Process each match
        for match in matches:
            start_index = match.end()
            end_index = html.find(delimiter, start_index)
            if end_index != -1:
                content = html[start_index:end_index]
                if re.search(r".*/.*-.*-.*-", content):
                    fullurl = url + content
                    article.add(fullurl)

        return list(article)


