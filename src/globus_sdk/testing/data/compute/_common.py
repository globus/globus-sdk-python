import uuid

USER_ID = str(uuid.uuid1())
NON_USER_ID = str(uuid.uuid1())

SUBSCRIPTION_ID = str(uuid.uuid1())

ENDPOINT_ID = str(uuid.uuid1())
ENDPOINT_ID_2 = str(uuid.uuid1())
ENDPOINT_ID_3 = str(uuid.uuid1())

FUNCTION_ID = str(uuid.uuid1())
FUNCTION_ID_2 = str(uuid.uuid1())
FUNCTION_NAME = "howdy_world"
FUNCTION_CODE = "410\n10\n04\n:gASVQAAAAAAAAACMC2hvd2R5X3dvc ..."

TASK_GROUP_ID = str(uuid.uuid1())
TASK_ID = str(uuid.uuid1())
TASK_ID_2 = str(uuid.uuid1())
TASK_DOC = {
    "task_id": TASK_ID,
    "status": "success",
    "result": "10000",
    "completion_t": "1677183605.212898",
    "details": {
        "os": "Linux-5.19.0-1025-aws-x86_64-with-glibc2.35",
        "python_version": "3.10.4",
        "dill_version": "0.3.5.1",
        "globus_compute_sdk_version": "2.3.2",
        "task_transitions": {
            "execution-start": 1692742841.843334,
            "execution-end": 1692742846.123456,
        },
    },
}
