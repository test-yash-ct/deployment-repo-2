from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/v1/_debug", tags=["debug"])


# Debug endpoints removed for production security.
# Internal state inspection should use secure observability tooling.
# If debug capabilities are required, they must be:
# 1. Protected by authentication middleware
# 2. Restricted to internal IP ranges
# 3. Disabled entirely in production environments
