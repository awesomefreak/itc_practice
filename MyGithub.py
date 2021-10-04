import base64
from MyRequests import request

class MyGithubException(Exception):
    """
    This class is the base of all exceptions raised by MyGithub
    """


class RateLimitExceededException(MyGithubException):
    """
    Exception raised when the rate limit is exceeded (when Github API replies with a 403 rate limit exceeded HTML status)
    """


class BadCredentialsException(MyGithubException):
    """
    Exception raised in case of bad credentials (when Github API replies with a 401 or 403 HTML status)
    """


class BadUserAgentException(MyGithubException):
    """
    Exception raised when request is sent with a bad user agent header (when Github API replies with a 403 bad user agent HTML status)
    """


class UnknownException(MyGithubException):
    """
    Exception raised when no other Exception worked
    """


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

    def github_request(self, url, headers, params, method):
        response = request(url, headers=headers, params=params, method=method)
        if response.status == 401 and response.get("message") == "Bad credentials":
            raise BadCredentialsException
        elif response.status == 403 and response.get("message").startswith(
            "Missing or invalid User Agent string"
        ):
            raise BadUserAgentException
        elif response.status == 403 and (
            response.get("message").lower().startswith("api rate limit exceeded")
            or response.get("message")
            .lower()
            .endswith("please wait a few minutes before you try again.")
        ):
            raise RateLimitExceededException
        elif response.status == 200:
            return response
        else:
            raise UnknownException


    def set_repo(self, owner, repo):
        assert owner and isinstance(owner, str)
        assert repo and isinstance(repo, str)
        self.owner = owner
        self.repo = repo

    def get_pulls(self, params):
        url = self.base_url + f"/repos/{self.owner}/{self.repo}/pulls"
        response = self.github_request(url, headers=self.headers, params=params, method="get")
        return response

    def get_issues(self, params):
        url = self.base_url + f"/repos/{self.owner}/{self.repo}/issues"
        response = self.github_request(url, headers=self.headers, params=params, method="get")
        return response

    def get_commits(self, params):
        url = self.base_url + f"/repos/{self.owner}/{self.repo}/commits"
        response = self.github_request(url, headers=self.headers, params=params, method="get")
        return response
