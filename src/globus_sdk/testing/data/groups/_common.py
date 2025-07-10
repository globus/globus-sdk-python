from __future__ import annotations

import typing as t
import uuid

GROUP_ID = str(uuid.uuid1())
USER_ID = str(uuid.uuid1())
SUBSCRIPTION_ID = str(uuid.uuid1())
SUBSCRIPTION_GROUP_ID = str(uuid.uuid1())
SUBSCRIPTION_INFO = {
    "name": "Golems R Us",
    "subscriber_name": "University of Chicago Golem Lab",
    "is_high_assurance": True,
    "is_baa": False,
    "connectors": {
        "052be037-7dda-4d20-b163-3077314dc3e6": {"is_ha": True, "is_baa": False},
        "1b6374b0-f6a4-4cf7-a26f-f262d9c6ca72": {"is_ha": True, "is_baa": False},
        "28ef55da-1f97-11eb-bdfd-12704e0d6a4d": {"is_ha": True, "is_baa": False},
        "49b00fd6-63f1-48ae-b27f-d8af4589f876": {"is_ha": True, "is_baa": False},
        "56366b96-ac98-11e9-abac-9cb6d0d9fd63": {"is_ha": True, "is_baa": False},
        "7251f6c8-93c9-11eb-95ba-12704e0d6a4d": {"is_ha": True, "is_baa": False},
        "7643e831-5f6c-4b47-a07f-8ee90f401d23": {"is_ha": True, "is_baa": False},
        "7c100eae-40fe-11e9-95a3-9cb6d0d9fd63": {"is_ha": True, "is_baa": False},
        "7e3f3f5e-350c-4717-891a-2f451c24b0d4": {"is_ha": True, "is_baa": False},
        "9436da0c-a444-11eb-af93-12704e0d6a4d": {"is_ha": True, "is_baa": False},
        "976cf0cf-78c3-4aab-82d2-7c16adbcc281": {"is_ha": True, "is_baa": False},
        "e47b6920-ff57-11ea-8aaa-000c297ab3c2": {"is_ha": True, "is_baa": False},
        "fb656a17-0f69-4e59-95ff-d0a62ca7bdf5": {"is_ha": True, "is_baa": False},
    },
}

BASE_GROUP_DOC: dict[str, t.Any] = {
    "name": "Claptrap's Rough Riders",
    "description": "No stairs allowed.",
    "parent_id": None,
    "id": GROUP_ID,
    "group_type": "regular",
    "enforce_session": False,
    "session_limit": 28800,
    "session_timeouts": {},
    "my_memberships": [
        {
            "group_id": GROUP_ID,
            "identity_id": USER_ID,
            "username": "claptrap@globus.org",
            "role": "member",
            "status": "active",
        }
    ],
    "policies": {
        "group_visibility": "private",
        "group_members_visibility": "managers",
    },
    "subscription_id": None,
    "subscription_info": None,
}

SUBSCRIPTION_GROUP_DOC: dict[str, t.Any] = {
    "name": "University of Chicago, Department of Magical Automata",
    "description": "The finest in machines that go 'ping!' and 'whomp!' and 'bzzt!'",
    "parent_id": None,
    "id": SUBSCRIPTION_GROUP_ID,
    "group_type": "plus",
    "enforce_session": True,
    "session_limit": 1800,
    "session_timeouts": {},
    "my_memberships": [
        {
            "group_id": SUBSCRIPTION_GROUP_ID,
            "identity_id": USER_ID,
            "username": "claptrap@globus.org",
            "role": "member",
            "status": "active",
        }
    ],
    "policies": {
        "group_visibility": "private",
        "group_members_visibility": "managers",
    },
    "subscription_id": SUBSCRIPTION_ID,
    "subscription_info": SUBSCRIPTION_INFO,
}
