from __future__ import annotations

import textwrap

from sqlalchemy import text
from sqlalchemy.engine import Result
from sqlalchemy.ext.asyncio import AsyncSession


def _sql_literal(s: str) -> str:
    return s.replace("'", "''")


def build_raw_search_sql(
    natural_q: str, team: str, owner: str, op: str, org_scope: str | None
) -> str:
    joiner = " OR " if (op or "and").lower() == "or" else " AND "
    frags: list[str] = []
    if natural_q:
        f = _sql_literal(natural_q)
        frags.append(f"body ilike '%{f}%'")
    if org_scope != "org" and team:
        frags.append(f"team_id = '{_sql_literal(team)}'")
    if org_scope != "org" and owner:
        frags.append(f"owner_id = '{_sql_literal(owner)}'")
    if not frags:
        where = "true"
    else:
        where = joiner.join(f"({x})" for x in frags)
    return textwrap.dedent(
        f"""
        select id, team_id, owner_id, title, body, md, created_at
        from search_documents
        where {where}
        """
    ).strip()


async def run_search(
    session: AsyncSession,
    natural_q: str,
    team: str,
    owner: str,
    op: str,
    org_scope: str | None,
) -> list[dict[str, object]]:
    # Removed raw SQL passthrough to prevent SQL injection
    sql = build_raw_search_sql(natural_q, team, owner, op, org_scope)
    res: Result = await session.execute(text(sql))
    rows: list[dict[str, object]] = []
    for m in res.mappings():
        rows.append(dict(m))
    return rows
