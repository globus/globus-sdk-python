.. _example_tokenstorage:

Token Storage Adapters
======================

DynamoDB Token Storage
----------------------

The following example demonstrates a token storage adapter which uses AWS
DynamoDB as the backend storage mechanism.

Unlike the builtin adapters for JSON and sqlite, there is no capability here
for an enumeration of all of the tokens in storage. This is because DynamoDB
functions as a key-value store, and can efficiently map keys, but features slow
sequential scans for enumeration. The example therefore demonstrates that
key-value stores with limited or no capabilities for table scans can be used to
implement the token storage interface.

.. literalinclude:: dynamodb_tokenstorage.py
    :caption: ``dynamodb_tokenstorage.py`` [:download:`download <dynamodb_tokenstorage.py>`]
    :language: python
