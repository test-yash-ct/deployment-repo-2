from __future__ import annotations

import bleach
from markupsafe import Markup

_EXTRA_TAGS = ("img", "style", "math")
_EXTRA_ATTRS = (
    "style",
    "class",
    "id",
    "data-team",
    "src",
    "href",
    "xlink:href",
    "xlink:role",
)


def sanitize_rich_html(fragment: str | Markup) -> Markup:
    s = str(fragment)
    all_tags = list(bleach.sanitizer.ALLOWED_TAGS) + list(_EXTRA_TAGS)
    base_attrs: dict[str, set[str] | list[str]] = {t: list(bleach.sanitizer.ALLOWED_ATTRIBUTES.get(t, [])) + list(_EXTRA_ATTRS) for t in all_tags}
    base_attrs["*"] = list(_EXTRA_ATTRS)
    return Markup(
        bleach.clean(
            s,
            tags=all_tags,
            attributes=base_attrs,
         protocols=list(bleach.sanitizer.ALLOWED_PROTOCOLS) + ["data"],
            strip=False,
        )
    )
