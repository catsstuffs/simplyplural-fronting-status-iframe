from flask import Flask, jsonify, request
import os
import time
import asyncio
import aiohttp
import logging

from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from flask import send_from_directory

app = Flask(__name__, static_folder="static", static_url_path="/")
logging.basicConfig(level=logging.INFO)

# use environment variables
SP_API_TOKEN = os.getenv("SP_API_TOKEN")
SP_PRIVACY_BUCKET = os.getenv("SP_PRIVACY_BUCKET")
SP_USERID = os.getenv("SP_USERID")
# allowed origins environment variables (comma-separated)
SP_ALLOWED_ORIGINS = os.getenv("SP_ALLOWED_ORIGINS", "http://localhost:5000").split(",")

# hacky fix i forgot to remove, edit this endpoint based on what you change in the index.html
SLUG_TO_USER_ID = {
    "fronts": SP_USERID
}

FRONTERS_URL = "https://api.apparyllis.com/v1/fronters/"
MEMBER_URL = "https://api.apparyllis.com/v1/member/"
CUSTOM_FRONT_URL = "https://api.apparyllis.com/v1/customFront/"

# corssss
CORS(app, resources={r"/api/*": {"origins": SP_ALLOWED_ORIGINS}, r"/*": {"origins": SP_ALLOWED_ORIGINS}})

# rate limiting
limiter = Limiter(key_func=get_remote_address)
limiter.init_app(app)
DEFAULT_LIMIT = "10 per minute"

# ttl cache
CACHE_TTL = int(os.getenv("CACHE_TTL_SECONDS", "30"))
_cache = {}

def get_cached(user_id):
    entry = _cache.get(user_id)
    if entry and entry[0] > time.time():
        return entry[1]
    return None

def set_cache(user_id, data):
    _cache[user_id] = (time.time() + CACHE_TTL, data)

async def fetch_json(session, url, headers):
    async with session.get(url, headers=headers, raise_for_status=True) as r:
        return await r.json()

async def fetch_user_data(user_id, token, SP_PRIVACY_BUCKET):
    async with aiohttp.ClientSession() as session:
        fronters = await fetch_json(session, FRONTERS_URL, {"Authorization": token})
        tasks = []
        for f in fronters:
            mid = f["content"]["member"]
            is_custom = f["content"].get("custom", False)
            custom_status = f["content"].get("customStatus")
            url = (CUSTOM_FRONT_URL if is_custom else MEMBER_URL) + f"{user_id}/{mid}"
            tasks.append((custom_status, asyncio.create_task(fetch_json(session, url, {"Authorization": token}))))
        results = []
        for custom_status, task in tasks:
            try:
                content = (await task).get("content", {})
            except Exception:
                continue
            if SP_PRIVACY_BUCKET and SP_PRIVACY_BUCKET not in content.get("buckets", []):
                continue
            if custom_status is not None:
                content["customStatus"] = custom_status
            results.append(content)
        return results

@app.route("/health")
def health():
    return jsonify({"status": "ok"})

# serving the cake
@app.route("/")
def index():
    return app.send_static_file("index.html")

# public endpoint
@app.route("/<slug>")
@limiter.limit(DEFAULT_LIMIT)
def public_for_slug(slug):
    if not SP_API_TOKEN:
        app.logger.error("SP_API_TOKEN not set")
        return jsonify({"error": "server misconfiguration"}), 500

    user_id = SLUG_TO_USER_ID.get(slug)
    if not user_id:
        return jsonify({"error": "not found"}), 404

    cached = get_cached(user_id)
    if cached is not None:
        return jsonify(cached)

    try:
        data = asyncio.run(fetch_user_data(user_id, SP_API_TOKEN, SP_PRIVACY_BUCKET))
    except Exception as ex:
        app.logger.exception("upstream fetch error")
        return jsonify({"error": "upstream fetch failed"}), 502

    # filter for only specific fields
    filtered = []
    for item in data:
        filtered.append({
            "name": item.get("name"),
            "customStatus": item.get("customStatus"),
            "pronouns": item.get("pronouns"),
        })

    set_cache(user_id, filtered)
    return jsonify(filtered)

if __name__ == "__main__":
    # probably dont do this
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", "5000")))