import json
import logging
from logging import Logger

import requests
from requests import Response

logger: Logger = logging.getLogger(__name__)


class SimplePaNOSCClient:
    url: str
    username: str
    password: str

    def __init__(self, url: str, username: str, password: str) -> None:
        self.url = url
        self.username = username
        self.password = password

    def __generic_pss_call(self, url: str, method: str, data: dict = None) -> Response:
        basic_auth: tuple = (self.username, self.password) if self.username and self.password else None
        resp: Response = requests.request(method=method, url=url,
                                          **({"data": json.dumps(data)} if data else {}),
                                          **({"auth": basic_auth} if self.username and self.password else {}))
        return resp

    def item_exists(self, pss_id: str) -> bool:
        url: str = f"{self.url}/items/{pss_id}"
        resp: Response = self.__generic_pss_call(url=url, method="GET")

        return resp.status_code == 200
