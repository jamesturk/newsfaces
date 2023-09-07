from newsfaces.models import Image
import pathlib
import httpx


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
