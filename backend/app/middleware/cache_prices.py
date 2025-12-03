import os
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from urllib.parse import urlencode
from app.utils import cache

TTL = int(os.getenv("PHASE5_CACHE_TTL", "600"))

def _cache_key_from_request(request: Request) -> str:
    # key includes full query (provider/region/service, etc.)
    q = dict(request.query_params)
    return "phase5:prices:" + urlencode(sorted(q.items()))

class PricesCacheMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Only cache GETs to /v1/providers/prices
        if request.method == "GET" and request.url.path == "/v1/providers/prices":
            key = _cache_key_from_request(request)
            hit = cache.cache_get(key)
            if hit is not None:
                return JSONResponse(hit, status_code=200)

            # Not in cache → call the next app handler
            response: Response = await call_next(request)

            # Cache only successful JSON responses
            try:
                if response.status_code == 200 and response.media_type == "application/json":
                    # We have to read the body once; convert to dict if possible
                    body = b"".join([chunk async for chunk in response.body_iterator])
                    # Replace the consumed iterator with the raw body for downstream
                    response.body_iterator = iter([body])
                    # Attempt to decode to JSON; if not JSON, skip caching
                    import json
                    payload = json.loads(body.decode("utf-8"))
                    cache.cache_set(key, payload, ttl_seconds=TTL)
            except Exception:
                # On any error, skip caching silently
                pass

            return response

        # All other requests pass through
        return await call_next(request)
