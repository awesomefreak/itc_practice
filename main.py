import datetime
import argparse
from collections import defaultdict
from MyGithub import Github, MyGithubException

class RepoDataCollector:
    api = None
    # higher numbers might cause memory error
    COMMITS_MAX_RESULTS_PER_PAGE = 100
    PULLS_MAX_RESULTS_PER_PAGE = 30
    ISSUES_MAX_RESULTS_PER_PAGE = 50

    def __init__(self, api: Github):
        assert api
        self.api = api

    @staticmethod
    def datetime_to_str(datetime_obj):
        return datetime_obj.strftime('%Y-%m-%dT%H:%M:%S')

    @staticmethod
    def _run_request(request_func, params):
        try:
            response_data = request_func(params).json()
        except MyGithubException as e:
            print(e)
            response_data = []
        return response_data

    def _iterate_over_pages(self, request_func, params, max_iter=None):
        batch_response_data = []
        page_index = 1
        while True:
            params["page"] = page_index
            response_data = self._run_request(request_func, params)
            if response_data:
                batch_response_data.extend(response_data)
                if not max_iter or page_index <= max_iter:
                    page_index += 1
                else:
                    break
            else:
                break
        return batch_response_data

    def get_commits(self, date_start=None, date_end=None, branch=None):
        params = {
            "per_page": self.COMMITS_MAX_RESULTS_PER_PAGE,
        }
        if date_start and isinstance(date_start, datetime.datetime):
            params["since"] = self.datetime_to_str(date_start)
        if date_end and isinstance(date_end, datetime.datetime):
            params["until"] = self.datetime_to_str(date_end)

        if branch and isinstance(branch, str):
            params["sha"] = branch
        commits_data = self._iterate_over_pages(
            self.api.get_commits, params)
        return commits_data

    def get_pull_requests(self, branch=None):
        params = {
            "state": "all",
            "per_page": self.PULLS_MAX_RESULTS_PER_PAGE,
        }
        if branch and isinstance(branch, str):
            params["base"] = branch
        pull_requests_data = self._iterate_over_pages(
            self.api.get_pulls, params)
        return pull_requests_data

    def get_issues(self, date_start=None):
        params = {
            "state": "all",
            "per_page": self.ISSUES_MAX_RESULTS_PER_PAGE,
        }
        if date_start and isinstance(date_start, datetime.datetime):
            params["since"] = self.datetime_to_str(date_start)
        issues_data = self._iterate_over_pages(
            self.api.get_issues, params)
        return issues_data



class GithubAnalytics:
    commits_data = None
    pull_requests_data = None
    issues_data = None

    def __init__(self, commits_data, pull_requests_data, issues_data):
        assert isinstance(commits_data, list)
        self.commits_data = commits_data
        assert isinstance(commits_data, list)
        self.pull_requests_data = pull_requests_data
        assert isinstance(commits_data, list)
        self.issues_data = issues_data

    @staticmethod
    def str_to_datetime(str_date):
        return datetime.datetime.strptime(
            str_date, '%Y-%m-%dT%H:%M:%SZ'
            )

    def get_opened_and_closed_objects(self, data, date_start, date_end):
        d = {
            "opened": 0,
            "closed": 0
        }
        for elem in data:
            created_at = elem.get("created_at")
            created_at = self.str_to_datetime(created_at)

            if (not date_start or date_start <= created_at) and (not date_end or created_at <= date_end):
                d["opened"] += 1
            if closed_at := elem.get("closed_at"):
                closed_at = self.str_to_datetime(closed_at)
                if (not date_start or date_start <= created_at) and (not date_end or created_at <= date_end):
                    d["closed"] += 1
        return d

    def get_retired_objects(self, data, date_end, days_for_retirement):
        retired_count = 0
        for elem in data:
            created_at = elem.get("created_at")
            created_at = self.str_to_datetime(created_at)
            if date_end - created_at > datetime.timedelta(days=days_for_retirement):
                if not elem.get("closed_at"):
                        retired_count += 1
                else:
                    closed_at = elem.get("closed_at")
                    closed_at = self.str_to_datetime(closed_at)
                    if closed_at > date_end:
                        retired_count += 1

        return retired_count

    def get_active_users(self, display_limit=30):
        """Task 1"""
        d = defaultdict(lambda: 0)
        for commit_data in self.commits_data:
            if commit_data.get("commit") and commit_data.get("commit").get("author") and commit_data.get("commit").get("author").get("name"):
                author_name = commit_data.get("commit").get("author").get("name")
                d[author_name] += 1
        # sorting and returning display_limit tuples of person name and number of commits
        active_users = [(k, v) for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)][:display_limit]

        print("Table of active users, based on number of commits")
        print(f"{'Username:': <20}|Number Of Commits:")
        for username, number_of_commits in active_users:
            print(f"{username: <20}|{number_of_commits}")
        print()

    def get_opened_and_closed_pull_requests(self, date_start, date_end):
        """Task 2"""
        opened_and_closed_pull_requests = self.get_opened_and_closed_objects(self.pull_requests_data, date_start, date_end)

        print(f"Number of opened pull requests: {opened_and_closed_pull_requests['opened']}")
        print(f"Number of closed pull requests: {opened_and_closed_pull_requests['closed']}\n")

    def get_retired_pull_requests(self, date_end, days_for_retirement=30):
        """Task 3"""
        retired_pull_requests_count = self.get_retired_objects(self.pull_requests_data, date_end, days_for_retirement)
        print(f"Number of retired pull requests: {retired_pull_requests_count}\n")

    def get_opened_and_closed_issues(self, date_start, date_end):
        """Task 4"""
        opened_and_closed_issues =  self.get_opened_and_closed_objects(self.issues_data, date_start, date_end)
        print(f"Number of opened issues: {opened_and_closed_issues['opened']}")
        print(f"Number of closed issues: {opened_and_closed_issues['closed']}\n")

    def get_retired_issues(self, date_end, days_for_retirement=14):
        """Task 5"""
        retired_issues_count = self.get_retired_objects(self.issues_data, date_end, days_for_retirement)
        print(f"Number of retired issues: {retired_issues_count}\n")

    def run_all_tasks(self, date_start, date_end):
        self.get_active_users()
        self.get_opened_and_closed_pull_requests(date_start, date_end)
        self.get_retired_pull_requests(date_end)
        self.get_opened_and_closed_issues(date_start, date_end)
        self.get_retired_issues(date_end)


def run(owner, repo, date_start=None, date_end=None, branch=None, token=None) -> None:
    if token:
        api = Github(login_or_token=token)
    else:
        api = Github()
    api.set_repo(owner, repo)

    data_collector = RepoDataCollector(api)
    commits_data = data_collector.get_commits(date_start=date_start, date_end=date_end, branch=branch)
    pull_requests_data = data_collector.get_pull_requests(branch=branch)
    issues_data = data_collector.get_issues()
    github_analytics = GithubAnalytics(
        commits_data=commits_data,
        pull_requests_data=pull_requests_data,
        issues_data=issues_data
    )
    github_analytics.run_all_tasks(date_start, date_end)

def str_to_datetime(string, is_start=True):
    try:
        if len(string) == 10:
            datetime_obj = datetime.datetime.strptime(string, '%Y-%m-%d')
            if not is_start:
                datetime_obj = datetime_obj.replace(hour=23, minute=59, second=59)
        elif len(string) == 19:
            datetime_obj = datetime.datetime.strptime(string, '%Y-%m-%dT%H:%M:%S')
        else:
            raise ValueError
    except ValueError:
        raise ValueError('Wrong date_start format, YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS are required')
    return datetime_obj

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-o", "--owner", help="Owner of repo as string", required=True)
    argParser.add_argument("-r", "--repo", help="Repository name as string", required=True)
    argParser.add_argument("-ds", "--date_start", help="Starting date in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format")
    argParser.add_argument("-de", "--date_end", help="End date in YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS format")
    argParser.add_argument("-b", "--branch", help="Branch name as string")
    argParser.add_argument("-t", "--token", help="Github token, for higher rate limit")

    args = argParser.parse_args()
    owner = args.owner
    repo = args.repo

    if args.date_start:
        date_start = str_to_datetime(args.date_start)
    else:
        date_start = None

    if args.date_end:
        date_end = str_to_datetime(args.date_end, is_start=False)
    else:
        date_end = None

    branch = args.branch
    token = args.token

    run(owner, repo, date_start, date_end, branch, token)