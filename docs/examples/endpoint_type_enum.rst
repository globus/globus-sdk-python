Transfer Endpoint Type Enum
---------------------------

If your application needs to support Globus Connect Server version 4 and
version 5, Globus Connect Personal, and Shared Endpoints, you may need to
determine what type of endpoint or collection you are handling.

The `Globus documentation site <https://docs.globus.org>`_ offers several references on
this subject, including `a section on this exact subject matter
<https://docs.globus.org/globus-connect-server/migrating-to-v5.4/application-migration/#determining_endpoint_or_collection_type>`_
and Transfer API documentation `describing the different types of endpoints
<https://docs.globus.org/api/transfer/endpoint/#types_of_endpoints>`_.

In python, the logic for doing this is easily expressed in the form of an enum
class for the different endpoint types, and a function which takes an Endpoint
Document (from the Transfer service) and returns the matching enum member.
The helper can be made a classmethod of the enum, encapsulating the logic in
one class, all as follows:

.. code-block:: python


    from enum import Enum, auto


    class TransferEndpointType(Enum):
        # Globus Connect Personal
        GCP = auto()
        # Globus Connect Server version 5 Endpoint
        GCSV5_ENDPOINT = auto()
        # GCSv5 collections
        GUEST_COLLECTION = auto()
        MAPPED_COLLECTION = auto()
        # a Shared Endpoint (also sometimes referred to as a Guest Collection
        # on Globus Connect Personal)
        SHARE = auto()
        # any other endpoint document is most likely GCSv4, but not necessarily
        # this technically includes legacy types of endpoints which are not GCSv4
        # most applications can treat this case as meaning "GCSv4"
        # in fact, the "nice_name" method below does so!
        NON_GCSV5_ENDPOINT = auto()

        @classmethod
        def nice_name(cls, eptype: TransferEndpointType) -> str:
            return {
                cls.GCP: "Globus Connect Personal",
                cls.GCSV5_ENDPOINT: "Globus Connect Server v5 Endpoint",
                cls.GUEST_COLLECTION: "Guest Collection",
                cls.MAPPED_COLLECTION: "Mapped Collection",
                cls.SHARE: "Shared Endpoint",
                cls.NON_GCSV5_ENDPOINT: "GCSv4 Endpoint",
            }.get(eptype, "UNKNOWN")

        @classmethod
        def determine_endpoint_type(cls, ep_doc: dict) -> TransferEndpointType:
            """
            Given an endpoint document from Transfer, determine what type of
            endpoint or collection it is
            """
            if ep_doc.get("is_globus_connect") is True:
                return cls.GCP

            if ep_doc.get("non_functional") is True:
                return cls.GCSV5_ENDPOINT

            has_host = ep_doc.get("host_endpoint_id") is not None

            if ep_doc.get("gcs_version"):
                try:
                    major, _minor, _patch = ep_doc["gcs_version"].split(".")
                except ValueError:  # split -> unpack didn't give 3 values
                    major = None

                gcsv5 = major == "5"
            else:
                gcsv5 = False

            if gcsv5:
                if has_host:
                    return cls.GUEST_COLLECTION
                else:
                    return cls.MAPPED_COLLECTION

            elif has_host:
                return cls.SHARE

            return cls.NON_GCSV5_ENDPOINT
