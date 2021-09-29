import base64
import json
from urllib import response
from MyRequests import request

class Github:
    headers = {
        "Accept": "application/vnd.github.v3+json"
    }
    base_url = None
    owner = None
    repo = None

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

    def set_repo(self, owner, repo):
        assert owner and isinstance(owner, str)
        assert repo and isinstance(repo, str)
        self.owner = owner
        self.repo = repo

    def get_pulls(self, params):
        url = self.base_url + f"/repos/{self.owner}/{self.repo}/pulls"
        response = request(url, headers=self.headers, params=params, method="get")
        return response

    def get_issues(self, params):
        url = self.base_url + f"/repos/{self.owner}/{self.repo}/issues"
        response = request(url, headers=self.headers, params=params, method="get")
        return response

    def get_commits(self, params):
        url = self.base_url + f"/repos/{self.owner}/{self.repo}/commits"
        response = request(url, headers=self.headers, params=params, method="get")
        return response
