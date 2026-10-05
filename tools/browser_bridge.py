"""Optional stdio HTTP transport for browser QA when loopback networking is blocked.

Chromium still renders the real application responses and owns the cookies.
No templates, assets, or database results are substituted.
"""

import base64
import json
import sys
from io import BytesIO
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app import create_app  # noqa: E402

client = create_app().test_client(use_cookies=False)
for line in sys.stdin:
    message = json.loads(line)
    data = base64.b64decode(message["body"])
    headers = message["headers"]
    if "formdata" in message:
        data = {}
        for entry in message["formdata"]:
            if "file" in entry:
                data[entry["key"]] = (
                    BytesIO(base64.b64decode(entry["file"])),
                    entry["filename"],
                    entry["type"],
                )
            else:
                data[entry["key"]] = entry["value"]
        headers = {
            key: value
            for key, value in headers.items()
            if key.lower() not in {"content-type", "content-length"}
        }
    response = client.open(
        path=message["url"],
        method=message["method"],
        headers=headers,
        data=data,
    )
    headers = {}
    for key in response.headers.keys():
        headers[key] = "\n".join(response.headers.getlist(key))
    sys.stdout.write(
        json.dumps(
            {
                "id": message["id"],
                "status": response.status_code,
                "headers": headers,
                "body": base64.b64encode(response.data).decode("ascii"),
            }
        )
        + "\n"
    )
    sys.stdout.flush()
