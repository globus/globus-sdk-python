import pytest


def test_extdoclink_renders_simple(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. extdoclink:: Create Demuddler
            :ref: demuddler/create
        """,
    )

    assert etree.tag == "document"

    paragraph = etree.find("paragraph")
    assert paragraph is not None
    text_parts = list(paragraph.itertext())
    assert "See " in text_parts[0]
    assert "API documentation for details" in text_parts[-1]

    link = paragraph.find("reference")
    assert link is not None
    assert link.text == "Create Demuddler"
    uri = link.get("refuri")
    assert uri is not None
    assert uri == "https://docs.globus.org/api/demuddler/create"


@pytest.mark.parametrize(
    "service, base_url",
    (
        ("groups", "https://groups.api.globus.org/redoc#operation"),
        ("gcs", "https://docs.globus.org/globus-connect-server/v5/api"),
        ("flows", "https://globusonline.github.io/globus-flows#tag"),
        ("compute", "https://compute.api.globus.org/redoc#tag"),
    ),
)
def test_extdoclink_renders_with_custom_service(sphinx_runner, service, base_url):
    etree = sphinx_runner.to_etree(
        f"""\
        .. extdoclink:: Battle Cry
            :ref: theTick/SPOOOON
            :service: {service}
        """,
    )

    assert etree.tag == "document"

    paragraph = etree.find("paragraph")
    assert paragraph is not None
    text_parts = list(paragraph.itertext())
    assert "See " in text_parts[0]
    assert "API documentation for details" in text_parts[-1]

    link = paragraph.find("reference")
    assert link is not None
    assert link.text == "Battle Cry"
    uri = link.get("refuri")
    assert uri is not None
    assert uri == f"{base_url}/theTick/SPOOOON"


def test_extdoclink_renders_with_custom_base_url(sphinx_runner):
    etree = sphinx_runner.to_etree(
        """\
        .. extdoclink:: Battle Cry
            :ref: SPOOOON
            :base_url: https://docs.globus.org/90sNostalgia/TheCity
        """,
    )

    assert etree.tag == "document"

    paragraph = etree.find("paragraph")
    assert paragraph is not None
    link = paragraph.find("reference")
    assert link is not None
    assert link.text == "Battle Cry"
    uri = link.get("refuri")
    assert uri is not None
    assert uri == "https://docs.globus.org/90sNostalgia/TheCity/SPOOOON"
