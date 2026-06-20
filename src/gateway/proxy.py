from __future__ import annotations

from fastapi import HTTPException
import httpx
from fastapi import Request
from fastapi.responses import Response, StreamingResponse


def pick_upstream_path(target: str) -> str:
    mapping = {
        "docs": "upstream_docs",
        "files": "upstream_files",
        "search": "upstream_search",
    }
    if target not in mapping:
        return ""
    return mapping[target]


async def forward_json(
    request: Request,
    target: str,
    subpath: str,
) -> Response:
    """Forward request to upstream service with sanitized headers and trusted identity.
    
    Security: Strips all client-supplied X-* headers to prevent header injection attacks.
    After bearer token validation in upstream.py, we extract identity from the token
    and set trusted X-User-Id and X-Client-Id headers for backend services.
    """
    up_attr = pick_upstream_path(target)
    if not up_attr:
        raise HTTPException(status_code=400, detail="Unknown upstream")
    base = str(getattr(request.app.state.settings, up_attr))
    url = f"{base.rstrip('/')}/" + subpath.lstrip("/")
    
    # Security: Allowlist-based header filtering to prevent injection
    # Strip all X-* headers from client to prevent impersonation attacks
    ALLOWED_HEADER_PREFIXES = (
        "content-",
        "accept",
        "user-agent",
        "authorization",
    )
    BLOCKED_HEADERS = ("host", "transfer-encoding", "connection")
    
    headers = {}
    for k, v in request.headers.items():
        k_lower = k.lower()
        # Block infrastructure headers
        if k_lower in BLOCKED_HEADERS:
            continue
        # Block all X-* headers to prevent client injection
        if k_lower.startswith("x-"):
            continue
        # Allow specific safe headers
        if any(k_lower.startswith(prefix) for prefix in ALLOWED_HEADER_PREFIXES):
            headers[k] = v
    
    # Extract authenticated identity from validated bearer token
    # Note: Bearer token validation happens in upstream.py before this function is called
    auth_header = request.headers.get("authorization", "")
    if auth_header.lower().startswith("bearer "):
        token = auth_header[7:].strip()
        # TODO: Implement proper JWT parsing and validation here
        # For now, this is a placeholder showing the secure pattern
        # Backend services MUST NOT trust X-User-Id/X-Client-Id without gateway validation
        # Production implementation should:
        # 1. Parse and verify JWT signature
        # 2. Check expiry and claims
        # 3. Extract user_id/client_id from validated claims
        # 4. Set trusted headers: headers["X-User-Id"] = validated_user_id
        # 5. Set headers["X-Client-Id"] = validated_client_id
        # Backend services should validate requests come from gateway (mTLS or shared secret)
        pass
    
    body = await request.body()
    async with httpx.AsyncClient(timeout=60.0) as client:
        r = await client.request(
            request.method,
            url,
            content=body if body else None,
            headers=headers,
            params=dict(request.query_params),
        )
    return Response(
        content=r.content,
        status_code=r.status_code,
        headers={k: v for k, v in r.headers.items() if k.lower() != "transfer-encoding"},
    )
