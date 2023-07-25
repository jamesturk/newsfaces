import requests
import lxml.html

def extract_html(url,article_selector,img_selector="img",p_selector=None,t_selector=None):
    """
    Extract the image and text content from and HTML:
    Inputs:
    - url(str): Url to parse
    - article_selector(str): css selector for article container
    - img_selector(str): css selector for images living inside the article 
    container
    - p_selector(str): css selector for paragraphs living inside the article container
    - t_selector(str): css selector for title living inside the article container
    Return:
    -imgs(lst): list where each element is an image represented as a tuple 
    with src, alt, title, and caption as elements
    - text(tuple): Tuple where the first element is the article text and the
    second element the title
    """
    resp = requests.get(url)
    root = lxml.html.fromstring(resp.text)  
    article_body = root.cssselect(article_selector)[0]
    imgs = extract_imgs(article_body,img_selector)
    text = extract_text(article_body,p_selector,t_selector)
    return imgs, text

def extract_imgs(html,selector = "img"):
    """
    Extract the image content from an HTML:
    Inputs:
    - html(str): html to extract images from
    - img_selector(str): css selector for images living inside the article 
    container
    Return:
    -imgs(lst): list where each element is an image represented as a tuple 
    with src, alt, title, and caption as elements
    """
    imgs = []
    images = html.cssselect(selector)
    for img in images:
        src = img.get("src")
        alt = img.get("alt")
        title = img.get("title")
        caption = img.get("caption")
        image = (src,alt,title, caption)
        imgs.append(image)
    return imgs

def extract_text(html,p_selector =None,t_selector=None):
    """
    Extract the text content from an HTML:
    Inputs:

    - p_selector(str): css selector for paragraphs living inside the article container
    - t_selector(str): css selector for title living inside the article container
    Return:
    - text(tuple): Tuple where the first element is the article text and the
    second element the title
    """
    p_text = None
    t_text = None
    if p_selector:
        paragraphs = html.cssselect(p_selector)
        if paragraphs:
            p_text = ""
            for p in paragraphs:
                p_text += p.text_content()

    if t_selector:
        t_text = html.cssselect(t_selector)[0].text

    text = (p_text,t_text)

    return text