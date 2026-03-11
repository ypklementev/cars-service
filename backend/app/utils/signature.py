import hmac
import hashlib
from http.client import HTTPException
from fastapi.requests import Request
from dotenv import load_dotenv
import os

load_dotenv()

SECRET = os.getenv("JWT_SECRET").encode()


def verify_signature(body: bytes, signature: str):

    expected = hmac.new(
        SECRET,
        body,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(signature, expected)


async def check_signature(request: Request):

    body = await request.body()
    signature = request.headers.get("X-Signature")

    if not signature or not verify_signature(body, signature):
        raise HTTPException(403, "Invalid signature")