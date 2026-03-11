import json
import hmac
import hashlib
from dotenv import load_dotenv
import os

load_dotenv()

SECRET = os.getenv("JWT_SECRET").encode()


def sign_payload(data: dict):

    payload = json.dumps(
        data,
        separators=(",", ":"),
        ensure_ascii=False
    ).encode()

    signature = hmac.new(
        SECRET,
        payload,
        hashlib.sha256
    ).hexdigest()

    return payload, signature