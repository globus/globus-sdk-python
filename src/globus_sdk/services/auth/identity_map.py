import uuid


def is_username(val):
    """
    If the value parses as a UUID, then it's an ID, not a username.
    If it does not parse as such, then it must be a username.
    """
    try:
        uuid.UUID(val)
        return False
    except ValueError:
        return True


def split_ids_and_usernames(identity_ids):
    ids = set()
    usernames = set()

    for val in identity_ids:
        if is_username(val):
            usernames.add(val)
        else:
            ids.add(val)

    return ids, usernames


class IdentityMap:
    r"""
    There's a common pattern of having a large batch of Globus Auth Identities which you
    want to inspect. For example, you may have a list of identity IDs fetched from
    Access Control Lists on Globus Endpoints. In order to display these identities to an
    end user, you may want to resolve them to usernames.

    However, naively looking up the identities one-by-one is very inefficient. It's best
    to do batched lookups with multiple identities at once. In these cases, an
    ``IdentityMap`` can be used to do those batched lookups for you.

    An ``IdentityMap`` is a mapping-like type which converts Identity IDs and Identity
    Names to Identity records (dictionaries) using the Globus Auth API.

    .. note::

        ``IdentityMap`` objects are not full Mappings in the same sense as python dicts
        and similar objects. By design, they only implement a small part of the Mapping
        protocol.

    The basic usage pattern is

    - create an ``IdentityMap`` with an AuthClient which will be used to call out to
      Globus Auth

    - seed the ``IdentityMap`` with IDs and Usernames via :py:meth:`~IdentityMap.add` (you
      can also do this during initialization)

    - retrieve identity IDs or Usernames from the map

    Because the map can be populated with a collection of identity IDs and Usernames
    prior to lookups being performed, it can improve the efficiency of these operations
    up to 100x over individual lookups.

    If you attempt to retrieve an identity which has not been previously added to the
    map, it will be immediately added. But adding many identities beforehand will
    improve performance.

    The ``IdentityMap`` will cache its results so that repeated lookups of the same Identity
    will not repeat work. It will also map identities both by ID and by Username,
    regardless of how they're initially looked up.

    .. warning::

        If an Identity is not found in Globus Auth, it will trigger a KeyError when
        looked up. Your code must be ready to handle KeyErrors when doing a lookup.

    Correct usage looks something like so::

        ac = globus_sdk.AuthClient(...)
        idmap = globus_sdk.IdentityMap(
            ac, ["foo@globusid.org", "bar@uchicago.edu"]
        )
        idmap.add("baz@xsede.org")
        # adding by ID is also valid
        idmap.add("c699d42e-d274-11e5-bf75-1fc5bf53bb24")
        # map ID to username
        assert (
            idmap["c699d42e-d274-11e5-bf75-1fc5bf53bb24"]["username"]
            == "go@globusid.org"
        )
        # map username to ID
        assert (
            idmap["go@globusid.org"]["id"]
            == "c699d42e-d274-11e5-bf75-1fc5bf53bb24"
        )

    And simple handling of errors::

        try:
            record = idmap["no-such-valid-id@example.org"]
        except KeyError:
            username = "NO_SUCH_IDENTITY"
        else:
            username = record["username"]

    or you may achieve this by using the :py:meth:`~.IdentityMap.get` method::

        # internally handles the KeyError and returns the default value
        record = idmap.get("no-such-valid-id@example.org", None)
        username = record["username"] if record is not None else "NO_SUCH_IDENTITY"

    :param auth_client: The client object which will be used for lookups against Globus Auth
    :type auth_client: :class:`AuthClient <globus_sdk.AuthClient>`
    :param identity_ids: A list or other iterable of usernames or identity IDs (potentially
        mixed together) which will be used to seed the ``IdentityMap`` 's tracking of
        unresolved Identities.
    :type identity_ids: iterable of str
    :param id_batch_size: A non-default batch size to use when communicating with Globus
        Auth. Leaving this set to the default is strongly recommended.
    :type id_batch_size: int, optional

    .. automethodlist:: globus_sdk.IdentityMap
        include_methods=__getitem__,__delitem__
    """  # noqa

    _default_id_batch_size = 100

    def __init__(self, auth_client, identity_ids=None, id_batch_size=None):
        self.auth_client = auth_client
        self.id_batch_size = id_batch_size or self._default_id_batch_size

        # uniquify, copy, and split into IDs vs usernames
        self.unresolved_ids, self.unresolved_usernames = split_ids_and_usernames(
            [] if identity_ids is None else identity_ids
        )

        # the cache is a dict mapping IDs and Usernames
        self._cache = {}

    def _fetch_batch_including(self, key):
        """
        Batch resolve identifiers (usernames or IDs), being sure to include the desired,
        named key. The key also determines which kind of batch will be built --
        usernames or IDs.

        Store the results in the internal cache.
        """
        # for whichever set of unresolved names is appropriate, build the batch to
        # lookup up to *at most* the batch size
        # also, remove the unresolved names from tracking so that they will not be
        # looked up again
        batch = []
        set_to_use = (
            self.unresolved_usernames if is_username(key) else self.unresolved_ids
        )
        for _ in range(0, min(self.id_batch_size - 1, len(set_to_use))):
            batch.append(set_to_use.pop())
        # avoid double-adding the provided key, but add it if it's missing
        if key not in batch:
            batch.append(key)
        else:
            try:
                batch.append(set_to_use.pop())
            except KeyError:  # empty set, ignore
                pass

        response = self.auth_client.get_identities(
            **(dict(usernames=batch) if is_username(key) else dict(ids=batch))
        )
        for x in response["identities"]:
            self._cache[x["id"]] = x
            self._cache[x["username"]] = x

    def add(self, identity_id):
        """
        Add a username or ID to the ``IdentityMap`` for batch lookups later.

        Returns True if the ID was added for lookup.
        Returns False if it was rejected as a duplicate of an already known name.

        :param identity_id: A string Identity ID or Identity Name (a.k.a. "username") to
            add
        :type identity_id: str
        """
        if identity_id in self._cache:
            return False
        if is_username(identity_id):
            if identity_id in self.unresolved_usernames:
                return False
            else:
                self.unresolved_usernames.add(identity_id)
                return True
        if identity_id in self.unresolved_ids:
            return False
        self.unresolved_ids.add(identity_id)
        return True

    def get(self, key, default=None):
        """
        A dict-like get() method which accepts a default value.
        """
        try:
            return self[key]
        except KeyError:
            return default

    def __getitem__(self, key):
        """
        ``IdentityMap`` supports dict-like lookups with ``map[key]``
        """
        if key not in self._cache:
            self._fetch_batch_including(key)
        return self._cache[key]

    def __delitem__(self, key):
        """
        ``IdentityMap`` supports ``del map[key]``. Note that this only removes lookup
        values from the cache and will not impact the set of unresolved/pending IDs.
        """
        del self._cache[key]
