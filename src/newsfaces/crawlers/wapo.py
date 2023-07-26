class WashingtonPost_API(Crawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.washingtonpost.com/prism/api/prism-query?_website=washpost&query=%7B%22query%22%3A%22prism%3A%2F%2Fprism.query%2Fsite-articles-only%2C%2Fpolitics%26offset%3D600%26limit%3D30%22%7D"

    def crawl(self, base_page, article=set(), video=set()):
        """
        From an initial API query page, run through all possible
        API queries-- putting articles on the pages into
        a set.

        Returns:
        Set of articles
        """
        response = make_request(base_page)
        json_data = json.loads(response.text)
        for i in range(len(json_data)):
            url_text = json_data["items"][i]["canonical_url"]
            url = make_link_absolute(
                url_text, "https://www.washingtonpost.com/politics"
            )
            if url.startswith("https://www.washingtonpost.com/politics"):
                article.add(url)
            else:
                video.add(url)
        begin = base_page.find("offset") + 9
        end = base_page.find("%26limit")
        try:
            articlenumber = int(base_page[begin:end])
        except ValueError:
            articlenumber = 10000
        if articlenumber < 9960:
            articlenumber += 30
            articlenumber = str(articlenumber)
            rev_basepage = (
                base_page[0:begin]
                + articlenumber
                + base_page[end : (len(base_page) + 1)]
            )
            article, video = self.crawl(rev_basepage, article, video)
        return article, video


class WashingtonPost(WaybackCrawler):
    def __init__(self):
        super().__init__()
        self.start_url = "https://www.washingtonpost.com/politics/"
        self.selector = ["div.story-headline.pr-sm"]

    def get_archive_urls(self, url, selectors):
        articles = super().get_archive_urls(url, selectors)
        filtered_articles = [
            article
            for article in articles
            if "https://www.washingtonpost.com/politics/2" in article
        ]
        return filtered_articles
