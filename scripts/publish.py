import yaml
import json
import requests
import sys
import os

WP_URL = "https://boostlen.com/wp-json/wp/v2/verse"
USERNAME = os.getenv("WP_USERNAME")
PASSWORD = os.getenv("WP_PASSWORD")

def publish_yaml(path):
    with open(path, "r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    reference = data.get("reference")
    verse_text = data.get("verse")
    meaning = data.get("meaning")
    tags = ", ".join(data.get("tags", []))
    book = data.get("book")
    book_order = data.get("book_order")

    cross_refs_json = json.dumps(data.get("cross_refs", []))

payload = {
    "title": reference,
    "status": "publish",
    "fields": {
        "reference": reference,
        "verse": verse_text,
        "meaning": meaning,
        "cross_refs_json": cross_refs_json,
        "tags": tags,
        "book": book,
        "book_order": book_order
    }
}

    response = requests.post(
        WP_URL,
        auth=(USERNAME, PASSWORD),
        json=payload
    )

    print("Status:", response.status_code)
    print("Response:", response.text)


if __name__ == "__main__":
    yaml_path = sys.argv[1]
    publish_yaml(yaml_path)
