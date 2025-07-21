from xml.etree import ElementTree

import pytest

# tests below will check the exact contents of BaseClient params
# if BaseClient changes, this will need to update -- but that's rare enough to be
# acceptable
BASE_CLIENT_PARAMS = (
    "app",
    "app_scopes",
    "authorizer",
    "app_name",
    "base_url",
    "transport",
)


def test_copy_params_requires_an_argument(
    sphinxext, docutils_runner, register_temporary_directive
):

    register_temporary_directive("sdk-copy-params", sphinxext.directives.CopyParams)

    with pytest.raises(Exception, match=r"1 argument\(s\) required, 0 supplied\."):
        docutils_runner.to_etree(".. sdk-copy-params::")


def test_copy_params_finds_base_client_with_or_without_qualified_name(sphinx_runner):
    etree1 = sphinx_runner.to_etree(
        """\
        .. py:function:: build_client(**kwargs)

            .. sdk-sphinx-copy-params:: globus_sdk.BaseClient
        """,
    )
    etree2 = sphinx_runner.to_etree(
        """\
        .. py:function:: build_client(**kwargs)

            .. sdk-sphinx-copy-params:: BaseClient
        """,
    )

    # the source attribute records the temporary filenames used
    # it doesn't matter what we set them to; just normalize them to be the same
    etree1.set("source", "/dev/stdin")
    etree2.set("source", "/dev/stdin")

    # now render and compare equal
    doc1 = ElementTree.tostring(etree1)
    doc2 = ElementTree.tostring(etree2)

    assert doc1 == doc2


def test_copy_params_renders_params_of_base_client(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. py:function:: build_client(**kwargs)

            .. sdk-sphinx-copy-params:: globus_sdk.BaseClient
        """,
    )

    assert etree.tag == "document"

    parameters_field = etree.find("./desc/desc_content/field_list/field")
    assert parameters_field is not None
    assert parameters_field.find("field_name").text == "Parameters"

    parameters_list = parameters_field.find("./field_body/bullet_list")
    assert parameters_list is not None
    parameter_names = parameters_list.findall("./list_item/paragraph/literal_strong")

    assert len(parameter_names) == len(BASE_CLIENT_PARAMS)
    param_names = tuple(p.text for p in parameter_names)
    assert param_names == BASE_CLIENT_PARAMS


def test_copy_params_can_render_after_content(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. py:function:: build_client(priority: int = 0, **kwargs)

            .. sdk-sphinx-copy-params:: globus_sdk.BaseClient

                :param priority: How cool this client will be
        """,
    )

    assert etree.tag == "document"

    parameters_field = etree.find("./desc/desc_content/field_list/field")
    assert parameters_field is not None
    assert parameters_field.find("field_name").text == "Parameters"

    parameters_list = parameters_field.find("./field_body/bullet_list")
    assert parameters_list is not None
    parameter_names = parameters_list.findall("./list_item/paragraph/literal_strong")

    assert len(parameter_names) == len(BASE_CLIENT_PARAMS) + 1
    param_names = tuple(p.text for p in parameter_names)
    assert param_names == ("priority",) + BASE_CLIENT_PARAMS


def test_copy_params_can_render_before_content(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. py:function:: build_client(**kwargs, priority: int = 0)

            .. sdk-sphinx-copy-params:: globus_sdk.BaseClient

                <YIELD>
                :param priority: How cool this client will be
        """,
    )

    assert etree.tag == "document"

    parameters_field = etree.find("./desc/desc_content/field_list/field")
    assert parameters_field is not None
    assert parameters_field.find("field_name").text == "Parameters"

    parameters_list = parameters_field.find("./field_body/bullet_list")
    assert parameters_list is not None
    parameter_names = parameters_list.findall("./list_item/paragraph/literal_strong")

    assert len(parameter_names) == len(BASE_CLIENT_PARAMS) + 1
    param_names = tuple(p.text for p in parameter_names)
    assert param_names == BASE_CLIENT_PARAMS + ("priority",)


def test_copy_params_can_render_in_the_middle_of_content(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. py:function:: build_client(awesomeness: float, **kwargs, priority: int = 0)

            .. sdk-sphinx-copy-params:: globus_sdk.BaseClient

                :param awesomeness: The awesomeness quotient
                <YIELD>
                :param priority: How cool this client will be
        """,
    )

    assert etree.tag == "document"

    parameters_field = etree.find("./desc/desc_content/field_list/field")
    assert parameters_field is not None
    assert parameters_field.find("field_name").text == "Parameters"

    parameters_list = parameters_field.find("./field_body/bullet_list")
    assert parameters_list is not None
    parameter_names = parameters_list.findall("./list_item/paragraph/literal_strong")

    assert len(parameter_names) == len(BASE_CLIENT_PARAMS) + 2
    param_names = tuple(p.text for p in parameter_names)
    assert param_names == ("awesomeness",) + BASE_CLIENT_PARAMS + ("priority",)
