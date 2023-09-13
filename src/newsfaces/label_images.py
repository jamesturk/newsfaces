import re
import pathlib
import httpx
from deepface import DeepFace
from .models import Image
from .politicians import DONALD_TRUMP, JOE_BIDEN, HILLARY_CLINTON
from pydantic import BaseModel


class LabeledImage(BaseModel):
    label: dict


POLITICIANS = [DONALD_TRUMP, JOE_BIDEN, HILLARY_CLINTON]


def label_image(id_, image):
    """
    Create LabeledImage object from an Image object
    Input:
    image(Image): Image object
    return:
    LabeledImage object
    """
    # Check if image has a face in it and if not, skip labeling process
    n_faces = n_faces_in_image(id_, image)
    image_label = {}
    if n_faces == 0:
        image_label["no-face-recognized"] = None
        return LabeledImage(label=image_label)
    # Check if face in image matches the one of the politicians of interes
    else:
        # Check if image associated text mentions politician to filter down
        # the number of faces to check
        image_label = {}
        text_politicians = text_mentions_politician(image)
        if text_politicians:
            for politician in text_politicians:
                verify = DeepFace.verify(
                    img1_path=politician.image,
                    img2_path=str(get_image_path(id_, image)),
                )
                if verify["verified"]:
                    label_score = 1 - verify["distance"]
                    image_label[politician.name] = label_score
            return LabeledImage(label=image_label)
        else:
            for politician in POLITICIANS:
                verify = DeepFace.verify(
                    img1_path=politician.image,
                    img2_path=str(get_image_path(id_, image)),
                )
                if verify["verified"]:
                    label_score = 1 - verify["distance"]
                    image_label[politician.name] = label_score

            return LabeledImage(label=image_label)


def get_image_path(id_: str, image: Image) -> pathlib.Path:
    image_dir = pathlib.Path("images")
    image_dir.mkdir(exist_ok=True)

    jpeg_path = image_dir / f"{id_}.jpeg"
    png_path = image_dir / f"{id_}.png"

    # return image if it's already been downloaded
    if jpeg_path.exists():
        return jpeg_path
    if png_path.exists():
        return png_path

    # fetch image & save it
    resp = httpx.get(image.url).raise_for_status()
    if resp.headers["Content-Type"] == "image/jpeg":
        path = jpeg_path
    elif resp.headers["Content-Type"] == "image/png":
        path = png_path
    else:
        raise ValueError(f"Unknown image type: {resp.headers['Content-Type']}")

    path.write_bytes(resp.content)

    return path


def text_mentions_politician(image):
    """
    Checks if an image caption or alt text mentions a politician
    """
    politicians = set()
    for politician in POLITICIANS:
        regex = politician.name_to_regex()
        if image.caption:
            if re.search(regex, image.caption, re.IGNORECASE):
                politicians.add(politician)
        if image.alt_text:
            if re.search(regex, image.alt_text, re.IGNORECASE):
                politicians.add(politician)
    return politicians


def n_faces_in_image(id_, image):
    """
    Return the number of faces recognized in an image
    """
    try:
        emb = DeepFace.represent(str(get_image_path(id_, image)))
        return len(emb)
    except:
        return 0
