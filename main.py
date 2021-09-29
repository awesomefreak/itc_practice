import json
import datetime
from MyGithub import Github

class RepoDataCollector:
    api = None
    COMMITS_MAX_RESULTS_PER_PAGE = 100
    PULLS_MAX_RESULTS_PER_PAGE = 50
    ISSUES_MAX_RESULTS_PER_PAGE = 100

    def __init__(self, api: Github):
        assert api
        self.api = api

    def _iterate_over_pages(self, request_func, params, max_iter=None):
        batch_response_data = []
        page_index = 1
        while True:
            params["page"] = page_index
            response_data = request_func(params).json()
            if response_data and not page_index > max_iter:
                batch_response_data.extend(response_data)
                page_index += 1
            else:
                break
        return batch_response_data

    def get_active_users(self, date_start, date_end, branch=None):
        params = {
            "since": date_start.strftime('%Y-%m-%d'),
            "until": date_end.strftime('%Y-%m-%d'),
            "per_page": self.COMMITS_MAX_RESULTS_PER_PAGE,
        }
        if branch and isinstance(branch, str):
            params["sha"] = branch
        commits_data = self._iterate_over_pages(self.api.get_commits, params)
        return commits_data

    def get_pull_requests(self, date_start, date_end, branch=None):
        params = {
            "state": "all",
            "per_page": self.PULLS_MAX_RESULTS_PER_PAGE,
        }
        if branch and isinstance(branch, str):
            params["sha"] = branch
        pull_requests_data = self._iterate_over_pages(self.api.get_pulls, params)
        return pull_requests_data

    def get_issues(self, date_start, date_end, branch=None):
        params = {
            "state": "all",
            "since": date_start.strftime('%Y-%m-%d'),
            "per_page": self.ISSUES_MAX_RESULTS_PER_PAGE,
        }
        if branch and isinstance(branch, str):
            params["sha"] = branch
        issues_data = self._iterate_over_pages(self.api.get_issues, params)
        return issues_data
