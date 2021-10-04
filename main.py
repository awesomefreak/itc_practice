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
    def _run_request(request_func, params):
        try:
            response_data = request_func(params).json()
        except MyGithubException as e:
            print(e)
            response_data = {}
        return(response_data)

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
        if date_start and isinstance(date_start, datetime.date):
            params["since"] = date_start.strftime('%Y-%m-%d')
        if date_end and isinstance(date_end, datetime.date):
            params["until"] = date_end.strftime('%Y-%m-%d')

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
        if date_start and isinstance(date_start, datetime.date):
            params["since"] = date_start.strftime('%Y-%m-%d')
        issues_data = self._iterate_over_pages(
            self.api.get_issues, params)
        return issues_data


def get_opened_and_closed_objects(data, date_start, date_end):
    d = {
        "opened": 0,
        "closed": 0
    }
    for elem in data:
        created_at = elem.get("created_at")
        created_at = datetime.datetime.strptime(
            created_at, '%Y-%m-%dT%H:%M:%SZ'
            ).date()
        if date_start <= created_at <= date_end:
            d["opened"] += 1
        if closed_at := elem.get("closed_at"):
            closed_at = datetime.datetime.strptime(
                closed_at, '%Y-%m-%dT%H:%M:%SZ'
                ).date()
            if date_start <= closed_at <= date_end:
                d["closed"] += 1
    return d

def get_retired_objects(data, days_for_retirement):
    today = datetime.date.today()
    retired_count = 0
    for elem in data:
        if not elem.get("closed_at"):
            created_at = elem.get("created_at")
            created_at = datetime.datetime.strptime(
                created_at, '%Y-%m-%dT%H:%M:%SZ'
                ).date()
            if today - created_at > datetime.timedelta(days=days_for_retirement):
                retired_count += 1
    return retired_count

def get_active_users(commits_data, display_limit=30):
    """Task 1"""
    d = defaultdict(lambda: 0)
    for commit_data in commits_data:
        commit = commit_data.get("commit")
        assert commit
        author = commit.get("author")
        assert author
        author_name = author.get("name")
        assert author_name
        d[author_name] += 1
    # sorting and returning display_limit tuples of person name and number of commits
    return [(k, v) for k, v in sorted(d.items(), key=lambda item: item[1], reverse=True)][:display_limit]

def get_opened_and_closed_pull_requests(pull_requests_data, date_start, date_end):
    """Task 2"""
    return get_opened_and_closed_objects(pull_requests_data, date_start, date_end)

def get_retired_pull_requests(pull_requests_data, days_for_retirement=30):
    """Task 3"""
    return get_retired_objects(pull_requests_data, days_for_retirement)

def get_opened_and_closed_issues(issues_data, date_start, date_end):
    """Task 4"""
    return get_opened_and_closed_objects(issues_data, date_start, date_end)

def get_retired_issues(issues_data, days_for_retirement=14):
    """Task 5"""
    return get_retired_objects(issues_data, days_for_retirement)

def run(owner, repo, date_start=None, date_end=None, branch=None) -> None:
    token = "YOUR_API_TOKEN"
    api = Github(token)
    api.set_repo(owner, repo)

    data_collector = RepoDataCollector(api)
    commits_data = data_collector.get_commits(date_start=date_start, date_end=date_end, branch=branch)
    pull_requests_data = data_collector.get_pull_requests(branch=branch)
    issues_data = data_collector.get_issues()

    active_users = get_active_users(commits_data)
    print("Table of active users, based on number of commits")
    print(f"{'Username:': <20}|Number Of Commits:")
    for username, number_of_commits in active_users:
        print(f"{username: <20}|{number_of_commits}")
    print()


    data = get_opened_and_closed_pull_requests(pull_requests_data, date_start, date_end)
    print(f"Number of opened pull requests: {data['opened']}")
    print(f"Number of closed pull requests: {data['closed']}\n")

    retired_count = get_retired_pull_requests(pull_requests_data)
    print(f"Number of retired pull requests: {retired_count}\n")

    data = get_opened_and_closed_issues(issues_data, date_start, date_end)
    print(f"Number of opened issues: {data['opened']}")
    print(f"Number of closed issues: {data['closed']}\n")

    retired_count = get_retired_pull_requests(issues_data)
    print(f"Number of retired issues: {retired_count}\n")

if __name__ == "__main__":
    argParser = argparse.ArgumentParser()
    argParser.add_argument("-o", "--owner", help="Owner of repo as string", required=True)
    argParser.add_argument("-r", "--repo", help="Repository name as string", required=True)
    argParser.add_argument("-ds", "--date_start", help="Starting date in YYYY-MM-DD format")
    argParser.add_argument("-de", "--date_end", help="End date in YYYY-MM-DD format")
    argParser.add_argument("-b", "--branch", help="Branch name as string")

    args = argParser.parse_args()

    owner = args.owner
    assert owner and isinstance(owner, str)
    repo = args.repo
    assert repo and isinstance(repo, str)
    date_start = None
    if args.date_start:
        try:
            date_start = datetime.datetime.strptime(args.date_start, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError('Wrong date_start format, YYYY-MM-DD is required')
    date_end = None
    if args.date_end:
        try:
            date_end = datetime.datetime.strptime(args.date_end, '%Y-%m-%d').date()
        except ValueError:
            raise ValueError('Wrong date_end format, YYYY-MM-DD is required')
    branch = args.branch
    assert branch and isinstance(branch, str)

    run(owner, repo, date_start, date_end, branch)