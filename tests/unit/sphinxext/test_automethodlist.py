from xml.etree import ElementTree

import pytest


def test_automethodlist_requires_an_argument(
    sphinxext, docutils_runner, register_temporary_directive
):

    register_temporary_directive(
        "automethodlist", sphinxext.custom_directives.AutoMethodList
    )

    with pytest.raises(Exception, match=r"1 argument\(s\) required, 0 supplied\."):
        docutils_runner.to_etree(".. automethodlist::")


# choose an arbitrary object from the SDK and confirm that `automethodlist`
# will render one of its public methods
# for this case, we're using `GlobusApp.login_required()`
def test_automethodlist_of_globus_app_shows_login(sphinx_runner):
    etree = sphinx_runner.to_etree(".. automethodlist:: globus_sdk.GlobusApp")

    assert etree.tag == "document"

    paragraph_element = etree.find("paragraph")
    assert paragraph_element is not None

    emphasized_text = paragraph_element.find("strong")
    assert emphasized_text is not None
    assert emphasized_text.text == "Methods"

    method_list = etree.find("bullet_list")
    assert method_list is not None
    assert b"login_required()" in ElementTree.tostring(method_list)
