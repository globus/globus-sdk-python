CHANGELOG
=========

v2.0.3
------

* Fix a packaging bug in version 2.0.2 which led to files being incorrectly
  included in the wheel release

v2.0.2
------

* Add support for python3.10

v2.0.1
------

* Remove support for python2 (`#396`_, `#397`_, `#398`_)

.. _#398: https://github.com/globus/globus-sdk-python/pull/398
.. _#397: https://github.com/globus/globus-sdk-python/pull/397
.. _#396: https://github.com/globus/globus-sdk-python/pull/396

v1.11.0
-------

* Add support for task skipped errors via
  `TransferClient.task_skipped_errors` and
  `TransferClient.endpoint_manager_task_skipped_errors` (`#393`_)
* Internal maintenance (`#389`_, `#390`_, `#391`_, `#392`_)

.. _#393: https://github.com/globus/globus-sdk-python/pull/393
.. _#392: https://github.com/globus/globus-sdk-python/pull/392
.. _#391: https://github.com/globus/globus-sdk-python/pull/391
.. _#390: https://github.com/globus/globus-sdk-python/pull/390
.. _#389: https://github.com/globus/globus-sdk-python/pull/389

v1.10.0
-------

* Add support for pyinstaller installation of globus-sdk (`#387`_)

.. _#387: https://github.com/globus/globus-sdk-python/pull/387

v1.9.1
------

* Fix `GlobusHTTPResponse` to handle responses with no `Content-Type` header (`#375`_)

.. _#375: https://github.com/globus/globus-sdk-python/pull/375

v1.9.0
------

* Add `globus_sdk.IdentityMap`, a mapping-like object for Auth ID lookups (`#367`_)
* Minor documentation and build improvements (`#369`_, `#362`_)
* Don't append trailing slashes when no path is given to a low-level client method like `get()` (`#364`_)
* Add `external_checksum` and `checksum_algorithm` to `TransferData.add_item()` named arguments (`#365`_)

.. _#367: https://github.com/globus/globus-sdk-python/pull/367
.. _#362: https://github.com/globus/globus-sdk-python/pull/362
.. _#369: https://github.com/globus/globus-sdk-python/pull/369
.. _#364: https://github.com/globus/globus-sdk-python/pull/364
.. _#365: https://github.com/globus/globus-sdk-python/pull/365

v1.8.0
------

* Add a property to paginated results which shows if more results are available (`#346`_)
* Update docs to state that Globus SDK uses semver (`#357`_)
* Fix `RefreshTokenAuthorizer` to handle a new `refresh_token` being sent back by Auth (`#359`_)
* Fix typo in endpoint_search log message (`#355`_)
* Fix Globus Web App activation links in docs (`#356`_)

.. _#359: https://github.com/globus/globus-sdk-python/pull/359
.. _#357: https://github.com/globus/globus-sdk-python/pull/357
.. _#356: https://github.com/globus/globus-sdk-python/pull/356
.. _#355: https://github.com/globus/globus-sdk-python/pull/355
.. _#346: https://github.com/globus/globus-sdk-python/pull/346

v1.7.1
------

* Allow arbitrary keyword args to `TransferData.add_item()` and `DeleteData.add_item()`, which passthrough to the item bodies (`#339`_)
* Minor internal improvements (`#342`_, `#343`_)

.. _#343: https://github.com/globus/globus-sdk-python/pull/343
.. _#342: https://github.com/globus/globus-sdk-python/pull/342
.. _#339: https://github.com/globus/globus-sdk-python/pull/339

v1.7.0
------

* Add `get_task` and `get_task_list` to `SearchClient` (`#335`_, `#336`_)
* Internal maintenance and testing improvements (`#331`_, `#334`_, `#333`_)

.. _#336: https://github.com/globus/globus-sdk-python/pull/336
.. _#335: https://github.com/globus/globus-sdk-python/pull/335
.. _#334: https://github.com/globus/globus-sdk-python/pull/334
.. _#333: https://github.com/globus/globus-sdk-python/pull/333
.. _#331: https://github.com/globus/globus-sdk-python/pull/331

v1.6.1
------

* Replace egg distribution format with wheels (`#314`_)
* Internal maintenance

.. _#314: https://github.com/globus/globus-sdk-python/pull/314

v1.6.0
------

* Correct handling of environment="production" as an argument to client construction (`#307`_)
* RenewingAuthorizer and its subclasses now expose the check_expiration_time method (`#309`_)
* Allow parameters to be passed to customize the request body of ConfidentialAppAuthClient.oauth2_get_dependent_tokens (`#308`_)
* Use sha256 hashes of tokens (instead of last 5 chars) in debug logging (`#305`_)
* Add the patch() method to BaseClient and its subclasses, sending an HTTP PATCH request (`#302`_)
* Officially add support for python 3.7 (`#300`_)
* Make pickling SDK objects safer (but still not officially supported!) (`#284`_)
* Malformed SDK usage may now raise GlobusSDKUsageError instead of ValueError. GlobusSDKUsageError inherits from ValueError (`#281`_)
* Numerous documentation improvements (`#279`_, `#294`_, `#296`_, `#297`_)

.. _#309: https://github.com/globus/globus-sdk-python/pull/309
.. _#308: https://github.com/globus/globus-sdk-python/pull/308
.. _#307: https://github.com/globus/globus-sdk-python/pull/307
.. _#305: https://github.com/globus/globus-sdk-python/pull/305
.. _#302: https://github.com/globus/globus-sdk-python/pull/302
.. _#300: https://github.com/globus/globus-sdk-python/pull/300
.. _#297: https://github.com/globus/globus-sdk-python/pull/297
.. _#296: https://github.com/globus/globus-sdk-python/pull/296
.. _#294: https://github.com/globus/globus-sdk-python/pull/294
.. _#284: https://github.com/globus/globus-sdk-python/pull/284
.. _#281: https://github.com/globus/globus-sdk-python/pull/281
.. _#279: https://github.com/globus/globus-sdk-python/pull/279

v1.5.0
------

* Add support for retrieving a local Globus Connect Personal endpoint's UUID (`#276`_)
* Fix bug in search client parameter handling (`#274`_)

.. _#276: https://github.com/globus/globus-sdk-python/pull/276
.. _#274: https://github.com/globus/globus-sdk-python/pull/274

v1.4.1
------

* Send `Content-Type: application/json` on requests with JSON request bodies (`#266`_)
* Support connection timeouts. Default timeout of 60 seconds (`#264`_)

.. _#266: https://github.com/globus/globus-sdk-python/pull/266
.. _#264: https://github.com/globus/globus-sdk-python/pull/264

v1.4.0
------

* Access token response data by way of scope name (`#261`_)
* Make `cryptography` a strict requirement, globus-sdk[jwt] is no longer necessary (`#257`_, `#260`_)
* Simplify OAuthTokenResponse.decode_id_token to not require the client as an argument (`#255`_)
* Add (beta) SearchClient class (`#259`_)

.. _#261: https://github.com/globus/globus-sdk-python/pull/261
.. _#260: https://github.com/globus/globus-sdk-python/pull/260
.. _#259: https://github.com/globus/globus-sdk-python/pull/259
.. _#257: https://github.com/globus/globus-sdk-python/pull/257
.. _#255: https://github.com/globus/globus-sdk-python/pull/255

v1.3.0
------

* Improve error message when installation onto python2.6 is attempted (`#245`_)
* Raise errors on client instantiation when `GLOBUS_SDK_ENVIRONMENT` appears to be invalid, support `GLOBUS_SDK_ENVIRONMENT=preview` (`#247`_)

.. _#245: https://github.com/globus/globus-sdk-python/pull/245
.. _#247: https://github.com/globus/globus-sdk-python/pull/247

v1.2.2
------

* Allow client classes to accept `base_url` as an argument to `__init__()` (`#241`_)
* Fix packaging to not include testsuite (`#232`_)
* Improve docs on `TransferClient` helper classes (`#231`_, `#233`_)

.. _#241: https://github.com/globus/globus-sdk-python/pull/241
.. _#233: https://github.com/globus/globus-sdk-python/pull/233
.. _#232: https://github.com/globus/globus-sdk-python/pull/232
.. _#231: https://github.com/globus/globus-sdk-python/pull/231

v1.2.1
------

* Use PyJWT instead of python-jose for JWT support (`#227`_)

.. _#227: https://github.com/globus/globus-sdk-python/pull/227

v1.2.0
------

* Add Transfer symlink support (`#218`_)
* Better handle UTF-8 inputs (`#208`_)
* Fix endpoint manager resume (`#224`_)
* Doc Updates & Minor Improvements

.. _#224: https://github.com/globus/globus-sdk-python/pull/224
.. _#218: https://github.com/globus/globus-sdk-python/pull/218
.. _#208: https://github.com/globus/globus-sdk-python/pull/208

v1.1.1
------

* Use correct paging style when making `endpoint_manager_task_list` calls (`#210`_)

.. _#210: https://github.com/globus/globus-sdk-python/pull/210

v1.1.0
------

* Add endpoint_manager methods to TransferClient (`#191`_, `#199`_, `#200`_, `#201`_, `#203`_)
* Change "identities_set" to "identity_set" for token introspection (`#163`_)
* Fix docs references to `oauth2_start_flow_*` (`#190`_)
* Support iterable requested_scopes everywhere (`#185`_)
* Add python 3.6 to supported platforms (`#180`_)
* Remove "Beta" from docs (`#179`_)
* Update dev status classifier to 5, prod (`#178`_)
* Numerous improvements to testsuite

.. _#203: https://github.com/globus/globus-sdk-python/pull/203
.. _#201: https://github.com/globus/globus-sdk-python/pull/201
.. _#200: https://github.com/globus/globus-sdk-python/pull/200
.. _#199: https://github.com/globus/globus-sdk-python/pull/199
.. _#191: https://github.com/globus/globus-sdk-python/pull/191
.. _#190: https://github.com/globus/globus-sdk-python/pull/190
.. _#185: https://github.com/globus/globus-sdk-python/pull/185
.. _#180: https://github.com/globus/globus-sdk-python/pull/180
.. _#179: https://github.com/globus/globus-sdk-python/pull/179
.. _#178: https://github.com/globus/globus-sdk-python/pull/178
.. _#163: https://github.com/globus/globus-sdk-python/pull/163

v1.0.0
------

* Adds `AuthAPIError` with more flexible error payload handling (`#175`_)

.. _#175: https://github.com/globus/globus-sdk-python/pull/175

v0.7.2
------

* Add `AuthClient.validate_token` (`#172`_)
* Bugfix for `on_refresh` users of `RefreshTokenAuthorizer` and `ClientCredentialsAuthorizer` (`#173`_)

.. _#173: https://github.com/globus/globus-sdk-python/pull/173
.. _#172: https://github.com/globus/globus-sdk-python/pull/172

v0.7.1
------

* Remove deprecated `oauth2_start_flow_*` methods (`#170`_)
* Add the `ClientCredentialsAuthorizer` (`#164`_)
* Add `jwt` extra install target. `pip install "globus_sdk[jwt]"` installs `python-jose` (`#169`_)

.. _#170: https://github.com/globus/globus-sdk-python/pull/170
.. _#169: https://github.com/globus/globus-sdk-python/pull/169
.. _#164: https://github.com/globus/globus-sdk-python/pull/164

v0.7.0
------

* Make `OAuthTokenResponse.decode_id_token()` respect `ssl_verify=no` configuration (`#161`_)
* Remove all properties of `OAuthTokenResponse` other than `by_resource_server` (`#162`_)

.. _#162: https://github.com/globus/globus-sdk-python/pull/162
.. _#161: https://github.com/globus/globus-sdk-python/pull/161

v0.6.0
------

* Opt out of the Globus Auth behavior where a `GET` of an identity username will provision that identity (`#145`_)
* Fixup OAuth2 PKCE to be spec-compliant (`#154`_)
* Wrap some `requests` network-related errors in custom exceptions (`#155`_)
* Add `deadline` support to `TransferData` and `DeleteData` (`#159`_)

.. _#159: https://github.com/globus/globus-sdk-python/pull/159
.. _#155: https://github.com/globus/globus-sdk-python/pull/155
.. _#154: https://github.com/globus/globus-sdk-python/pull/154
.. _#145: https://github.com/globus/globus-sdk-python/pull/145

v0.5.1
------

* Add support for the `prefill_named_grant` option to the Native App authorization flow (`#143`_)
* Unicode string improvements (`#129`_)
* Better handle unexpected error payloads (`#135`_)

.. _#143: https://github.com/globus/globus-sdk-python/pull/143
.. _#135: https://github.com/globus/globus-sdk-python/pull/135
.. _#129: https://github.com/globus/globus-sdk-python/pull/129
