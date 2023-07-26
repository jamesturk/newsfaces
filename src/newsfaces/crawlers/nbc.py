#Util Functions
from urllib.parse import urlparse
from crawlers.utils import make_request, parse_html, make_link_absolute, page_grab 
from crawlers.utils import crawl_wayback, create_csv, get_urls
import re
url = 'https://www.nbcnews.com/politics/'

def get_nbc(url, session=None):
    response = make_request(url, session=None)

    # Retrieve the raw HTML content
    html = response.text
    # Define the pattern and delimiter
    pattern = f'href="{url}'

    delimiter = '"'

    # Find all matches of the pattern in the HTML content
    matches = re.finditer(pattern, html)
    article=set()
    # Process each match
    for match in matches:
        start_index = match.end()
        end_index = html.find(delimiter, start_index)
        if end_index != -1:
            content = html[start_index:end_index]
            if re.search(r".*/.*-.*-.*-", content):
                fullurl=url+content
                article.add(fullurl)
    
    return list(article)
get_nbc(url)