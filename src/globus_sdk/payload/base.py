from __future__ import annotations

import typing as t
import warnings

import attrs

from globus_sdk import utils


def _validate_extra_against_model(
    instance: Payload,
    attribute: attrs.Attribute[t.Any],  # pylint: disable=unused-argument
    value: dict[str, t.Any] | utils.MissingType,
) -> None:
    """
    Validate the 'extra' field of a Payload object against the model defined by the
    Payload (sub)class.

    This is done by checking that none of the keys in the extra dict are also defined as
    fields on the class. If any such fields are found, a RuntimeWarning is emitted --
    such usage is and always will be supported, but users are advised to prefer the
    "real" fields whenever possible.
    """
    if isinstance(value, utils.MissingType):
        return

    model = instance.__class__
    model_fields = set(attrs.fields_dict(model))
    extra_fields = set(value.keys())

    redundant_fields = model_fields & extra_fields
    if redundant_fields:
        warnings.warn(
            f"'extra' keys overlap with defined fields for '{model.__qualname__}'. "
            "'extra' will take precedence during serialization. "
            f"redundant_fields={redundant_fields}",
            RuntimeWarning,
            stacklevel=2,
        )


@attrs.define(kw_only=True)
class Payload:
    """
    Payload objects are used to represent the data for a request.

    The 'extra' field is always defined, and can be used to store a dict of additional
    data which will be merged with the Payload object before it is sent in a request.
    """

    extra: dict[str, t.Any] | utils.MissingType = attrs.field(
        default=utils.MISSING, validator=_validate_extra_against_model
    )

    def asdict(self) -> dict[str, t.Any]:
        data = attrs.asdict(self)
        if data["extra"] is not utils.MISSING:
            data.update(data.pop("extra"))
        return data
