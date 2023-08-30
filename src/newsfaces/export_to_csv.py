import csv
from newsfaces.pipeline import pipeline

with open("images.csv", "w") as f:
    fields = [
        "article_id",
        "article_title",
        "image_url",
        "image_caption",
        "image_alt_text",
        "image_type",
    ]
    dw = csv.DictWriter(f, fields)

    for row in pipeline._grab_rows(["article"], max_items=100000, offset=0):
        for img in row["images"]:
            dw.writerow(
                dict(
                    article_id=row["id"],
                    article_title=row["title"],
                    image_url=img["url"],
                    image_caption=img["caption"],
                    image_alt_text=img["alt_text"],
                    image_type=str(img["image_type"]),
                )
            )
