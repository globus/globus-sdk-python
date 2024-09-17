import pytest

from globus_sdk._testing import construct_error
from globus_sdk.exc import ErrorSubdocument, RemovedInV4Warning
from globus_sdk.gare import (
    GARE,
    GlobusAuthorizationParameters,
    _variants,
    has_gares,
    is_gare,
    to_gare,
    to_gares,
)


@pytest.mark.parametrize(
    "alias, value",
    (
        ("GlobusAuthorizationParameters", GlobusAuthorizationParameters),
        ("GlobusAuthRequirementsError", GARE),
        ("to_auth_requirements_error", to_gare),
        ("to_auth_requirements_errors", to_gares),
        ("has_auth_requirements_errors", has_gares),
        ("is_auth_requirements_error", is_gare),
    ),
)
def test_deprecated_experimental_alias(alias, value):
    with pytest.warns(RemovedInV4Warning):
        from globus_sdk.experimental import (
            auth_requirements_error as experimental_module,
        )

        aliased_value = getattr(experimental_module, alias)
    assert aliased_value is value


@pytest.mark.parametrize(
    "error_dict, status",
    (
        (
            {
                "code": "ConsentRequired",
                "message": "Missing required foo_bar consent",
                "request_id": "WmMV97A1w",
                "required_scopes": [
                    "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
                ],
                "resource": "/transfer",
            },
            403,
        ),
        (
            {
                "code": "ConsentRequired",
                "required_scope": (
                    "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
                ),
                "description": "Missing required foo_bar consent",
            },
            401,
        ),
    ),
)
def test_create_auth_requirements_error_from_consent_error(error_dict, status):
    """
    Test that various ConsentRequired error shapes can be detected and converted
    to a GlobusAuthRequirementsError.
    """
    # Create various supplementary objects representing this error
    error_subdoc = ErrorSubdocument(error_dict)
    api_error = construct_error(body=error_dict, http_status=status)

    for error in (error_dict, error_subdoc, api_error):
        # Test boolean utility functions
        assert is_gare(error)
        assert has_gares([error])

        # Check that this only produces one error
        assert len(to_gares([error])) == 1

        # Create a Globus Auth requirements error from a Transfer format error
        authreq_error = to_gare(error)
        assert isinstance(authreq_error, GARE)
        assert authreq_error.code == "ConsentRequired"
        assert authreq_error.authorization_parameters.required_scopes == [
            "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
        ]
        assert (
            authreq_error.authorization_parameters.session_message
            == "Missing required foo_bar consent"
        )


@pytest.mark.parametrize(
    "authorization_parameters",
    (
        {
            "session_message": (
                "To gain access you need to authenticate with your baz identity"
            ),
            "session_required_identities": ["urn:globus:auth:identity:baz"],
            "session_required_mfa": True,
        },
        {
            "session_message": (
                "You need to authenticate with an identity that "
                "matches the required policies"
            ),
            "session_required_policies": ["foo", "baz"],
        },
        {
            "session_message": (
                "You need to authenticate with an identity that "
                "belongs to an authorized domain"
            ),
            "session_required_single_domain": ["foo.com", "baz.org"],
        },
        {
            "session_message": "You need to re-authenticate",
            "session_required_single_domain": ["foo.com", "baz.org"],
            "prompt": "login",
        },
    ),
)
def test_create_auth_requirements_error_from_authorization_error(
    authorization_parameters,
):
    """
    Test that various authorization parameters error shapes can be detected and
    converted to a GlobusAuthRequirementsError.
    """
    # Create various supplementary objects representing this error
    error_dict = {"authorization_parameters": authorization_parameters}
    error_subdoc = ErrorSubdocument(error_dict)
    api_error = construct_error(body=error_dict, http_status=403)

    for error in (error_dict, error_subdoc, api_error):
        # Test boolean utility functions
        assert is_gare(error)
        assert has_gares([error])

        # Check that this only produces one error
        assert len(to_gares([error])) == 1

        # Create a Globus Auth requirements error from a legacy
        # authorization parameters format error
        authreq_error = to_gare(error)
        assert isinstance(authreq_error, GARE)

        # Check that the default error code is set
        assert authreq_error.code == "AuthorizationRequired"

        # Iterate over the expected attributes and check that they match
        for name, value in authorization_parameters.items():
            assert getattr(authreq_error.authorization_parameters, name) == value


@pytest.mark.parametrize(
    "authorization_parameters",
    (
        {
            "session_message": (
                "You need to authenticate with an identity that "
                "matches the required policies"
            ),
            "session_required_policies": ["foo", "baz"],
        },
        {
            "session_message": (
                "You need to authenticate with an identity that "
                "belongs to an authorized domain"
            ),
            "session_required_single_domain": ["foo.com", "baz.org"],
        },
    ),
)
def test_create_auth_requirements_error_from_authorization_error_csv(
    authorization_parameters,
):
    """
    Test that authorization parameters error shapes that provide lists as comma-
    delimited values can be detected and converted to a GlobusAuthRequirementsError
    normalizing to lists of strings for those values.
    """
    # Create various supplementary objects representing this error
    error_dict = {"authorization_parameters": {}}
    for key, value in authorization_parameters.items():
        if key in ("session_required_policies", "session_required_single_domain"):
            # Convert the list to a comma-separated string for known variants
            error_dict["authorization_parameters"][key] = ",".join(value)
        else:
            error_dict["authorization_parameters"][key] = value

    error_subdoc = ErrorSubdocument(error_dict)
    api_error = construct_error(body=error_dict, http_status=403)

    for error in (error_dict, error_subdoc, api_error):
        # Test boolean utility functions
        assert is_gare(error)
        assert has_gares([error])

        # Check that this only produces one error
        assert len(to_gares([error])) == 1

        # Create a Globus Auth requirements error from a legacy
        # authorization parameters format error
        authreq_error = to_gare(error)
        assert isinstance(authreq_error, GARE)

        # Check that the default error code is set
        assert authreq_error.code == "AuthorizationRequired"

        # Iterate over the expected attributes and check that they match
        for name, value in authorization_parameters.items():
            assert getattr(authreq_error.authorization_parameters, name) == value


def test_create_auth_requirements_errors_from_multiple_errors():
    """
    Test that a GlobusAPIError with multiple subdocuments is converted to multiple
    GlobusAuthRequirementsErrors, and additionally test that this is correct even
    when mingled with other accepted data types.
    """
    consent_errors = construct_error(
        body={
            "errors": [
                {
                    "code": "ConsentRequired",
                    "message": "Missing required foo_bar consent",
                    "authorization_parameters": {
                        "required_scopes": [
                            "urn:globus:auth:scope:transfer.api.globus.org:all[*bar]"
                        ],
                        "session_message": "Missing required foo_bar consent",
                    },
                },
                {
                    "code": "ConsentRequired",
                    "message": "Missing required foo_baz consent",
                    "authorization_parameters": {
                        "required_scopes": [
                            "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
                        ],
                        "session_message": "Missing required foo_baz consent",
                    },
                },
            ]
        },
        http_status=403,
    )

    authorization_error = construct_error(
        body={
            "authorization_parameters": {
                "session_message": (
                    "You need to authenticate with an identity that "
                    "matches the required policies"
                ),
                "session_required_policies": ["foo", "baz"],
            }
        },
        http_status=403,
    )

    not_an_error = construct_error(
        body={
            "code": "NotAnError",
            "message": "This is not an error",
        },
        http_status=403,
    )

    all_errors = [consent_errors, not_an_error, authorization_error]

    # Test boolean utility function
    assert has_gares(all_errors)

    # Create auth requirements errors from a all errors
    authreq_errors = to_gares(all_errors)
    assert isinstance(authreq_errors, list)
    assert len(authreq_errors) == 3

    # Check that errors properly converted
    for authreq_error in authreq_errors:
        assert isinstance(authreq_error, GARE)

    # Check that the proper auth requirements errors were produced
    assert authreq_errors[0].code == "ConsentRequired"
    assert authreq_errors[0].authorization_parameters.required_scopes == [
        "urn:globus:auth:scope:transfer.api.globus.org:all[*bar]"
    ]
    assert (
        authreq_errors[0].authorization_parameters.session_message
        == "Missing required foo_bar consent"
    )
    assert authreq_errors[1].code == "ConsentRequired"
    assert authreq_errors[1].authorization_parameters.required_scopes == [
        "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
    ]
    assert (
        authreq_errors[1].authorization_parameters.session_message
        == "Missing required foo_baz consent"
    )
    assert authreq_errors[2].code == "AuthorizationRequired"
    assert authreq_errors[2].authorization_parameters.session_required_policies == [
        "foo",
        "baz",
    ]
    assert authreq_errors[2].authorization_parameters.session_message == (
        "You need to authenticate with an identity that matches the required policies"
    )


def test_create_auth_requirements_error_from_legacy_authorization_error_with_code():
    """
    Test that legacy authorization parameters error shapes that provide a `code` can be
    detected and converted to a GlobusAuthRequirementsError while retaining the `code`.
    """
    # Create a legacy authorization parameters error with a code
    error_dict = {
        "code": "UnsatisfiedPolicy",
        "authorization_parameters": {
            "session_message": (
                "You need to authenticate with an identity that "
                "matches the required policies"
            ),
            "session_required_policies": "foo,baz",
        },
    }

    # Create various supplementary objects representing this error
    error_subdoc = ErrorSubdocument(error_dict)
    api_error = construct_error(body=error_dict, http_status=403)

    for error in (error_dict, error_subdoc, api_error):
        # Test boolean utility functions
        assert is_gare(error)
        assert has_gares([error])

        # Check that this only produces one error
        assert len(to_gares([error])) == 1

        # Create a Globus Auth requirements error from a legacy
        # authorization parameters format error
        authreq_error = to_gare(error)
        assert isinstance(authreq_error, GARE)

        # Check that the custom error code is set
        assert authreq_error.code == "UnsatisfiedPolicy"

        # Iterate over the expected attributes and check that they match
        assert authreq_error.authorization_parameters.session_required_policies == [
            "foo",
            "baz",
        ]


def test_backward_compatibility_consent_required_error():
    """
    Test that a consent required error with a comingled backward-compatible
    data schema is converted to a GlobusAuthRequirementsError.
    """
    # Create an API error with a backward compatible data schema using
    # distinct values for duplicative fields to facilitate testing
    # (in practice these would be the same)
    error = construct_error(
        body={
            "code": "ConsentRequired",
            "message": "Missing required foo_bar consent",
            "request_id": "WmMV97A1w",
            "required_scopes": [
                "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
            ],
            "resource": "/transfer",
            "authorization_parameters": {
                "session_message": "Missing baz consent",
                "required_scopes": [
                    "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
                ],
                "optional": "A non-canonical field",
            },
        },
        http_status=403,
    )

    # Test boolean utility functions
    assert is_gare(error)
    assert has_gares([error])

    # Check that this only produces one error
    assert len(to_gares([error])) == 1

    # Create a Globus Auth requirements error
    authreq_error = to_gare(error)
    assert isinstance(authreq_error, GARE)
    assert authreq_error.code == "ConsentRequired"
    assert authreq_error.authorization_parameters.required_scopes == [
        "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
    ]
    assert (
        authreq_error.authorization_parameters.session_message == "Missing baz consent"
    )

    # Test that only suppotred fields are present in the dict
    assert authreq_error.to_dict() == {
        "code": "ConsentRequired",
        "authorization_parameters": {
            "session_message": "Missing baz consent",
            "required_scopes": [
                "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
            ],
        },
    }

    # Test that extra fields are present in the dict
    assert authreq_error.to_dict(include_extra=True) == {
        "code": "ConsentRequired",
        "message": "Missing required foo_bar consent",
        "request_id": "WmMV97A1w",
        "required_scopes": [
            "urn:globus:auth:scope:transfer.api.globus.org:all[*foo *bar]"
        ],
        "resource": "/transfer",
        "authorization_parameters": {
            "session_message": "Missing baz consent",
            "required_scopes": [
                "urn:globus:auth:scope:transfer.api.globus.org:all[*baz]"
            ],
            "optional": "A non-canonical field",
        },
    }


@pytest.mark.parametrize(
    "target_class, data, expect_message",
    [
        (  # missing 'code'
            GARE,
            {"authorization_parameters": {"session_required_policies": "foo"}},
            "'code' must be a string",
        ),
        (  # missing 'authorization_parameters'
            _variants.LegacyAuthorizationParametersError,
            {},
            (
                "'authorization_parameters' must be a 'LegacyAuthorizationParameters' "
                "object or a dictionary"
            ),
        ),
        (  # missing 'code'
            _variants.LegacyConsentRequiredTransferError,
            {"required_scopes": []},
            "'code' must be the string 'ConsentRequired'",
        ),
        (  # missing 'code'
            _variants.LegacyConsentRequiredAPError,
            {"required_scope": "foo"},
            "'code' must be the string 'ConsentRequired'",
        ),
    ],
)
def test_error_from_dict_insufficient_input(target_class, data, expect_message):
    """ """
    with pytest.raises(ValueError) as exc_info:
        target_class.from_dict(data)

    assert str(exc_info.value) == expect_message


@pytest.mark.parametrize(
    "target_class",
    [
        GlobusAuthorizationParameters,
        _variants.LegacyAuthorizationParameters,
    ],
)
def test_authorization_parameters_from_empty_dict(target_class):
    """ """
    authorization_params = target_class.from_dict({})
    assert authorization_params.to_dict() == {}
