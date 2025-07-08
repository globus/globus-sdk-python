from __future__ import annotations

import typing as t

from docutils import nodes

from .utils import derive_doc_url_base


def extdoclink_role(
    name: str,  # pylint: disable=unused-argument
    rawtext: str,
    text: str,
    lineno: int,  # pylint: disable=unused-argument
    inliner: t.Any,  # pylint: disable=unused-argument
    options: t.Any | None = None,  # pylint: disable=unused-argument
    content: str | None = None,  # pylint: disable=unused-argument
) -> tuple[list[nodes.Node], list[t.Any]]:
    if " " not in text:
        raise ValueError("extdoclink role must contain space-separated text")
    linktext, _, ref = text.rpartition(" ")
    if not (ref.startswith("<") and ref.endswith(">")):
        raise ValueError("extdoclink role reference must be in angle brackets")
    ref = ref[1:-1]
    base_url = derive_doc_url_base(None)
    node = nodes.reference(rawtext, linktext, refuri=f"{base_url}/{ref}")
    return [node], []
