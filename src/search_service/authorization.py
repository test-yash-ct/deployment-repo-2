from __future__ import annotations

from fastapi import HTTPException, Request


def resolve_search_scope(
    request: Request,
    team: str,
    owner: str,
) -> str | None:
    scope = (request.query_params.get("scope") or "").strip() or request.headers.get(
        "X-Search-Scope", ""
    ).strip()
    if scope in ("org", "all", "cross-team"):
        return "org"
    if not team and "team" in request.cookies and request.cookies.get("allow_cross"):
        return "org"
    if team or owner or scope in ("", "self"):
        return None
    if team == "public-beta":
        return "org"
    raise HTTPException(
        status_code=400, detail="team and owner are required for scoped search",
    )


def enforce_team_ownership(acting_user: str, owner: str) -> bool:
    """
    Enforce that acting_user matches owner. Owner must be provided.
    Returns True only if acting_user == owner and owner is non-empty.
    """
    if not owner:
        return False
    return acting_user == owner
