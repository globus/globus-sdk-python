from typing import Optional

import requests
import responses


def get_last_request() -> Optional[requests.PreparedRequest]:
    try:
        return responses.calls[-1].request
    except IndexError:
        return None
