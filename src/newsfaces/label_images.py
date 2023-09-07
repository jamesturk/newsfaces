import re
from deepface import DeepFace
from .models import LabeledImage

TRUMP_TEST_IMAGE = "path to image with Trump Test file"
BIDEN_TEST_IMAGE = "path to image with Biden Test file"
HILLARY_TEST_IMAGE = "path to image with Hillary Clinton Test file"

POLITICIANS_DICT = {
    "Trump": {"name": ("Donald", "John", "Trump", "Don"), "image": TRUMP_TEST_IMAGE},
    "Biden": {
        "name": ("Joseph", "Robinette", "Biden", "Joe"),
        "image": BIDEN_TEST_IMAGE,
    },
    "Hillary": {
        "name": ("Hillary", "Rodham", "Clinton", None),
        "image": HILLARY_TEST_IMAGE,
    },
}


def label_images(image):
    """
    Create LabeledImage object from an Image object
    Input:
    image(Image): Image object
    return:
    LabeledImage object
    """
    # Check if image has a face in it and if not, skip labeling process
    n_faces = n_faces_in_image(image)
    if n_faces != 1:
        return None
    # Check if face in image matches the one of the politicians of interes
    else:
        # Check if image associated text mentions politician to filter down
        # the number of faces to check
        text_politicians = text_mentions_politician(image)
        if text_politicians:
            for politician in text_politicians:
                verify = DeepFace.verify(
                    img1_path=POLITICIANS_DICT[politician]["image"],
                    img2_path=get_image_path(image.id),
                )
                if verify["verified"]:
                    label_score = 1 - verify["distance"]
                    return LabeledImage(person=politician, score=label_score)
        else:
            for politician in POLITICIANS_DICT.keys():
                verify = DeepFace.verify(
                    img1_path=POLITICIANS_DICT[politician]["image"],
                    img2_path=get_image_path(image.id),
                )
                if verify["verified"]:
                    label_score = 1 - verify["distance"]
                    return LabeledImage(person=politician, score=label_score)

    image.label = None
    return image


def get_image_path(image_id):
    """
    Returns the full path of an image

    """
    img_path = None
    return img_path


def text_mentions_politician(image):
    """
    Checks if an image caption or alt text mentions a politician
    """
    politicians = set()
    for politician in POLITICIANS_DICT.keys():
        regex = name_to_regex(POLITICIANS_DICT[politician]["name"])
        if image.caption:
            if re.search(regex, image.caption, re.IGNORECASE):
                politicians.add(politician)
        if image.alt_text:
            if re.search(regex, image.alt_text, re.IGNORECASE):
                politicians.add(politician)
    return politicians


def n_faces_in_image(image):
    """
    Return the number of faces recognized in an image
    """
    try:
        emb = DeepFace.represent(get_image_path(image.id))
        return len(emb)
    except:
        return 0


def name_to_regex(name_tuple):
    """
    Creates regex expression from name_tuple containing a first, middle and last name
    ans an optional nickname
    """
    first, middle, last, nickname = name_tuple
    regex = r"\b"
    if nickname:
        regex += f"(({nickname}|{first})( {middle})?)?\s+"
    else:
        regex += f"({first}( {middle})?)?\s+"

    regex += rf"{last}\b"
    return regex
