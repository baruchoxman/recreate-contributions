import datetime
import os
import requests


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


SHELLS = {
    "bash": "sh",
    "powershell": "ps1",
}


def run_github_query(query, api_key):
    headers = {"Authorization": "Bearer {}".format(api_key)}
    request = requests.post(QUERY_API_URL, json={"query": query}, headers=headers)
    if request.status_code != 200:
        raise Exception(
            "Query failed to run by returning code of {}. {}".format(
                request.status_code, query
            )
        )
    return request.json()


def get_contrib_dates_from_query_res(query_res):
    contrib_weeks = query_res["data"]["user"]["contributionsCollection"][
        "contributionCalendar"
    ]["weeks"]
    for contrib_week in contrib_weeks:
        for contrib_date in contrib_week["contributionDays"]:
            yield (
                datetime.date.fromisoformat(contrib_date["date"]),
                int(contrib_date["contributionCount"]),
            )


def get_all_contib_dates(username_to_copy_from, start_date, api_key):
    today = datetime.date.today()
    contrib_dates = []
    while start_date <= today:
        end_date = start_date + datetime.timedelta(days=365)
        query = QUERY_TEMPLATE % (
            username_to_copy_from,
            start_date.isoformat(),
            end_date.isoformat(),
        )
        query_res = run_github_query(query, api_key)
        contrib_dates.extend(get_contrib_dates_from_query_res(query_res))
        start_date = end_date

    return contrib_dates


def request_user_input(prompt="> "):
    """Request input from the user and return what has been entered."""
    return input(prompt)


def fake_it(contrib_dates, username, repo, shell):
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

    template = template_bash if shell == "bash" else template_powershell

    strings = []
    for date, value in contrib_dates:
        if not value:
            continue
        for _ in range(value):
            strings.append(commit(date, shell))

    return template.format(repo, "".join(strings), GIT_URL, username)


def commit(commitdate, shell):
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

    template = template_bash if shell == "bash" else template_powershell

    commit_dt = datetime.datetime.combine(commitdate, datetime.time(12, 0, 0))

    return template.format(commit_dt.isoformat(), commit_dt.isoformat())


def save(output, filename):
    """Saves the list to a given filename"""
    with open(filename, "w") as f:
        f.write(output)
    os.chmod(filename, 0o755)  # add execute permissions


def main():
    current_username = request_user_input("Enter the GitHub username to update: ")

    username_to_copy_from = request_user_input(
        "Enter the GitHub username to copy contributions from: "
    )

    start_date = request_user_input(
        "Enter the start date for copying contributions (YYYY-MM-DD): "
    )
    start_date = datetime.date.fromisoformat(start_date)

    api_token = request_user_input(
        "Enter the API token for github "
        "(create at https://github.com/settings/tokens): "
    )

    default_repo_name = "contrib-copy-{}".format(username_to_copy_from)
    repo = request_user_input(
        "Enter the name of the repository to use (default: {}): ".format(
            default_repo_name
        )
    )
    repo = repo or default_repo_name

    shells_keys = frozenset(SHELLS.keys())
    shell = ""
    while shell not in shells_keys:
        shell = request_user_input(
            "Enter the target shell ({}): ".format(" or ".join(sorted(shells_keys)))
        )

    contrib_dates = get_all_contib_dates(username_to_copy_from, start_date, api_token)

    output = fake_it(contrib_dates, current_username, repo, "bash")

    output_filename = "recreate_contributions.{}".format(SHELLS[shell])
    save(output, output_filename)
    print("{} saved.".format(output_filename))
    print(
        "Create a new(!) repo named {0} at {1} and run the script".format(
            repo, GITHUB_BASE_URL
        )
    )


if __name__ == "__main__":
    main()
