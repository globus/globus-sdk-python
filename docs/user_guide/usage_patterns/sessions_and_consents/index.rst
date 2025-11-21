.. _userguide_sessions_and_consents:

Sessions & Consents
===================

Globus resources can be protected with fine-grained policies which require
authentication with specific accounts or which require periodic
reauthentication.
These policies are enforced via the authentication system, Globus Auth.

To satisfy a policy requirement, users need to be prompted to update their
**session** in Globus Auth.
In some cases, applications can be written to preemptively provide the right
authentication information, but especially with session expirations and
time-based policies, it is not always possible to prevent session related
errors from occurring.

Correctly handling a session error requires that you generally follow a
workflow of:

- define the operation to attempt (e.g., a function)
- run the operation
- catch any session errors
- redrive a login flow based on those errors
- run the operation again

Relatedly, missing consent for an operation is sometimes only detectable after
the operation has been attempted.
In these cases, trying an operation, prompting for consent, and retrying the
operation closely resembles the session handling workflow.

.. toctree::
    :caption: How to Manage Sessions & Consents with the SDK
    :maxdepth: 1

    handling_transfer_auth_params/index
    coalescing_requirements_errors/index
