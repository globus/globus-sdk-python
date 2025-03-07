from __future__ import annotations

import typing as t

import sphinx.application


def after_autodoc_signature_replace_MISSING_repr(  # pylint: disable=missing-param-doc,missing-type-doc  # noqa: E501
    app: sphinx.application.Sphinx,  # pylint: disable=unused-argument
    what: str,  # pylint: disable=unused-argument
    name: str,  # pylint: disable=unused-argument
    obj: object,  # pylint: disable=unused-argument
    options: t.Any,  # pylint: disable=unused-argument
    signature: str | None,
    return_annotation: str | None,
) -> tuple[str | None, str | None]:
    """
    convert <globus_sdk.MISSING> to MISSING in autodoc signatures

    :param signature: the signature after autodoc parsing/rendering
    :param return_annotation: the return type annotation, including the leading `->`,
        after autodoc parsing/rendering
    """
    if signature is not None:
        signature = signature.replace("<globus_sdk.MISSING>", "MISSING")
    if return_annotation is not None:
        return_annotation = return_annotation.replace("<globus_sdk.MISSING>", "MISSING")
    return signature, return_annotation
