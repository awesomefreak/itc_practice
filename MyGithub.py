import base64
import json
from urllib import response
from MyRequests import request

class Github:
    headers = {}
    base_url = None

    def __init__(self, login_or_token, password=None, base_url="https://api.github.com"):
        assert login_or_token and isinstance(login_or_token, str)
        assert password is None or isinstance(password, str)
        assert base_url and isinstance(base_url, str)

        self.base_url = base_url

        if password:
            login = login_or_token
            b64 = (
                base64.b64encode((f"{login}:{password}").encode("utf-8"))
                .decode("utf-8")
                .replace("\n", "")
            )
            auth_header = f"Basic {b64}"
        elif login_or_token:
            token = login_or_token
            auth_header = f"token {token}"
        self.headers['Authorization'] = auth_header
    
    def get_pulls(self, owner, repo):
        url = self.base_url + f"/repos/{owner}/{repo}/pulls"
        params = {"state": "all"}
        response = request(url, headers=self.headers, params=params, method="get")
        json_response = response.json()
        return json_response




