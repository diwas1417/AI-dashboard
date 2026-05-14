import os
import json
import uuid
from django.conf import settings


def save_extracted_json(data):
    json_dir = settings.MEDIA_ROOT / "extracted_json"
    os.makedirs(json_dir, exist_ok=True)

    filename = f"market_trend_{uuid.uuid4().hex}.json"
    filepath = json_dir / filename

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return filename, filepath
