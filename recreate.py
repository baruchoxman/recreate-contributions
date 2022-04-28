import argparse
import datetime
import enum
import os
import platform
import requests
from typing import Any, Iterator, List, Tuple


GITHUB_BASE_URL = "https://github.com/"
GIT_URL = "git@github.com"
QUERY_API_URL = "https://api.github.com/graphql"

QUERY_TEMPLATE = """
{
  user(login: "%s") {
    contributionsCollection(from: "%sT00:00:00Z", to: "%sT00:00:00Z") {
      contributionCalendar {
        totalContributions
        weeks {
          contributionDays {
            date
            contributionCount
          }
        }
      }
    }
  }
}
"""

CONTRIB_DATES_DELTA_IN_DAYS = 365


class Shells(enum.Enum):
    BASH = "bash"
    POWERSHELL = "powershell"


SHELL_SUFFIX = {
    Shells.BASH: "sh",
    Shells.POWERSHELL: "ps1",
}
SHELL = Shells.POWERSHELL if platform.system() == "Windows" else Shells.BASH


def run_github_query(query: str, api_key: str) -> Any:
    headers = {"Authorization": f"Bearer {api_key}"}
    request = requests.post(QUERY_API_URL, json={"query": query}, headers=headers)
    if request.status_code != 200:
        raise Exception(
            f"Query failed to run by returning code of {request.status_code}. {query}"
        )
    return request.json()


def get_contrib_dates_from_query_res(
    query_res: Any,
) -> Iterator[Tuple[datetime.date, int]]:
    contrib_weeks = query_res["data"]["user"]["contributionsCollection"][
        "contributionCalendar"
    ]["weeks"]
    for contrib_week in contrib_weeks:
        for contrib_date in contrib_week["contributionDays"]:
            yield (
                datetime.date.fromisoformat(contrib_date["date"]),
                int(contrib_date["contributionCount"]),
            )


def get_all_contib_dates(
    username_to_copy_from: str,
    start_date: datetime.date,
    final_date: datetime.date,
    api_key: str,
) -> List[Tuple[datetime.date, int]]:
    contrib_dates: List[Tuple[datetime.date, int]] = []
    while start_date <= final_date:
        end_date = start_date + datetime.timedelta(days=CONTRIB_DATES_DELTA_IN_DAYS)
        query = QUERY_TEMPLATE % (
            username_to_copy_from,
            start_date.isoformat(),
            end_date.isoformat(),
        )
        query_res = run_github_query(query, api_key)
        contrib_dates.extend(get_contrib_dates_from_query_res(query_res))
        start_date = end_date

    return contrib_dates


def fake_it(
    contrib_dates: List[Tuple[datetime.date, int]],
    username: str,
    repo: str,
    shell: Shells,
) -> str:
    template_bash = (
        "#!/usr/bin/env bash\n"
        "REPO={0}\n"
        "git init $REPO\n"
        "cd $REPO\n"
        "touch README.md\n"
        "git add README.md\n"
        "{1}\n"
        "git branch -M main\n"
        "git remote add origin {2}:{3}/$REPO.git\n"
        "git pull origin main\n"
        "git push -u origin main\n"
    )

    template_powershell = (
        "cd $PSScriptRoot\n"
        '$REPO="{0}"\n'
        "git init $REPO\n"
        "cd $REPO\n"
        "New-Item README.md -ItemType file | Out-Null\n"
        "git add README.md\n"
        "{1}\n"
        "git branch -M main\n"
        "git remote add origin {2}:{3}/$REPO.git\n"
        "git pull origin main\n"
        "git push -u origin main\n"
    )

    template = template_bash if shell == Shells.BASH else template_powershell

    strings = []
    for date, value in contrib_dates:
        if not value:
            continue
        for _ in range(value):
            strings.append(commit(date, shell))

    return template.format(repo, "".join(strings), GIT_URL, username)


def commit(commitdate: datetime.date, shell: Shells) -> str:
    template_bash = (
        """GIT_AUTHOR_DATE={0} GIT_COMMITTER_DATE={1} """
        """git commit --allow-empty -m """
        """"recreating contributions" > /dev/null\n"""
    )

    template_powershell = (
        """$Env:GIT_AUTHOR_DATE="{0}"\n$Env:GIT_COMMITTER_DATE="{1}"\n"""
        """git commit --allow-empty -m """
        """"recreating contributions" | Out-Null\n"""
    )

    template = template_bash if shell == Shells.BASH else template_powershell

    commit_dt = datetime.datetime.combine(commitdate, datetime.time(12, 0, 0))

    return template.format(commit_dt.isoformat(), commit_dt.isoformat())


def save(output: str, filename: str) -> None:
    """Saves the list to a given filename"""
    with open(filename, "w", encoding="utf-8") as output_file:
        output_file.write(output)
    os.chmod(filename, 0o755)  # add execute permissions


def recreate_contibutions(
    current_username: str,
    username_to_copy_from: str,
    start_date: str,
    api_token: str,
    repo: str,
) -> None:
    repo = repo or f"contrib-copy-{username_to_copy_from}"

    contrib_dates = get_all_contib_dates(
        username_to_copy_from,
        datetime.date.fromisoformat(start_date),
        datetime.date.today(),
        api_token,
    )

    output = fake_it(contrib_dates, current_username, repo, SHELL)

    output_filename = f"recreate_contributions.{SHELL_SUFFIX[SHELL]}"
    save(output, output_filename)
    print(f"{output_filename} saved.")
    print(
        f"Create a new(!) repo named {repo} at {GITHUB_BASE_URL} and run the generated script"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="Recreate contributions")
    parser.add_argument(
        "-u", "--username", required=True, help="GitHub username to update"
    )
    parser.add_argument(
        "-s",
        "--source",
        required=True,
        help="Source GitHub username to copy contributions from",
    )
    parser.add_argument(
        "-d",
        "--date",
        required=True,
        help="Start date for copying contributions (YYYY-MM-DD)",
    )
    parser.add_argument(
        "-t",
        "--apitoken",
        required=True,
        help="API token for github (create at https://github.com/settings/tokens)",
    )
    parser.add_argument(
        "-r",
        "--repo",
        help='Repository to use (will use "contrib-copy-<source username>" if not provided',
    )
    arguments = parser.parse_args()

    recreate_contibutions(
        arguments.username,
        arguments.source,
        arguments.date,
        arguments.apitoken,
        arguments.repo,
    )


if __name__ == "__main__":
    main()
