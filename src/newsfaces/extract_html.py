def extract_html(
    html, article_selector,img_p_selector, img_selector="img", p_selector=None,
    t_selector=None):
    """
    Extract the image and text content from and HTML:
    Inputs:
        - html(str): Full html of an artcile url
        - article_selector(str): css selector for article container
        - img_p_selector(str): css selector for the parent elements of images in article
        - img_selector(str): css selector for images living inside the article
        container
        - p_selector(str): css selector for paragraphs living inside the article container
        - t_selector(str): css selector for title living inside the article container
    Return:
        -imgs(lst): list where each element is an image represented as a dictionary
        with src, alt, title, and caption as fields
        - art_text(str): Article text
        - t_text(str): Title
    """
    article_body = html.cssselect(article_selector)[0]
    imgs = extract_imgs(article_body,img_p_selector,img_selector)
    art_text = extract_text(article_body, p_selector)
    if t_selector:
        t_text = html.cssselect(t_selector)[0].text
    return imgs, art_text, t_text

def extract_imgs(html, img_p_selector,img_selector="img"):
    """
    Extract the image content from an HTML:
    Inputs:
        - html(str): html to extract images from
        - img_p_selector(list): list of css selector for the parent elements of images in articles
        - img_selector(str): css selector for the image elements
        Return:
        -imgs(lst): list where each element is an image represented as a dictionary
        with src, alt, title, and caption as fields
    """
    imgs = []
    for selector in img_p_selector:
        img_container = html.cssselect(selector)
        for container in img_container:
            images = container.cssselect(img_selector)
            for img in images:
                img_item = {}
                img_item["src"] = img.get("src")
                img_item["alt"] = img.get("alt")
                img_item["title"] = img.get("title")
                img_item["caption"] = img.get("caption")
                imgs.append(img_item)
    return imgs


def extract_text(html, p_selector=None):
    """
    Extract the article text content from an HTML:
    Inputs:
        - p_selector(str): css selector for paragraphs living inside the article container
    Return:
        - text(str): Article text
    """
    text = None
    if p_selector:
        paragraphs = html.cssselect(p_selector)
        if paragraphs:
            text = ""
            for p in paragraphs:
                text += p.text_content()

    return text
