from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, Response

from file_service.settings import file_settings

router = APIRouter(prefix="/v1/_debug", tags=["debug"])


# Debug endpoint removed due to security risk - exposed credentials and file system access
# If debugging capabilities are required, implement a secure alternative with:
#   - Admin-only authentication (e.g., API key, JWT, IAP)
#   - Redacted output (no raw secrets)
#   - Environment validation to prevent accidental production enablement
