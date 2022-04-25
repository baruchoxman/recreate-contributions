import recreate
import datetime
import pytest


@pytest.mark.parametrize(
    "shell,expected",
    [
        (
            recreate.Shells.BASH,
            "GIT_AUTHOR_DATE=2020-01-01T12:00:00 "
            "GIT_COMMITTER_DATE=2020-01-01T12:00:00 "
            "git commit --allow-empty -m "
            '"recreating contributions" > /dev/null\n',
        ),
        (
            recreate.Shells.POWERSHELL,
            '$Env:GIT_AUTHOR_DATE="2020-01-01T12:00:00"\n'
            '$Env:GIT_COMMITTER_DATE="2020-01-01T12:00:00"\n'
            "git commit --allow-empty -m "
            '"recreating contributions" | Out-Null\n',
        ),
    ],
)
def test_commit(shell, expected):
    test_date = datetime.date(2020, 1, 1)
    res = recreate.commit(test_date, shell)
    assert res == expected


@pytest.mark.parametrize(
    "shell,expected",
    [
        (
            recreate.Shells.BASH,
            "#!/usr/bin/env bash\n"
            "REPO=testrepo\n"
            "git init $REPO\n"
            "cd $REPO\n"
            "touch README.md\n"
            "git add README.md\n"
            "GIT_AUTHOR_DATE=2020-01-01T12:00:00 GIT_COMMITTER_DATE=2020-01-01T12:00:00 "
            'git commit --allow-empty -m "recreating contributions" > /dev/null\n'
            "GIT_AUTHOR_DATE=2020-01-01T12:00:00 GIT_COMMITTER_DATE=2020-01-01T12:00:00 "
            'git commit --allow-empty -m "recreating contributions" > /dev/null\n'
            "GIT_AUTHOR_DATE=2020-01-03T12:00:00 GIT_COMMITTER_DATE=2020-01-03T12:00:00 "
            'git commit --allow-empty -m "recreating contributions" > /dev/null\n'
            "\n"
            "git branch -M main\n"
            "git remote add origin git@github.com:fakeuser/$REPO.git\n"
            "git pull origin main\n"
            "git push -u origin main\n",
        ),
        (
            recreate.Shells.POWERSHELL,
            "cd $PSScriptRoot\n"
            '$REPO="testrepo"\n'
            "git init $REPO\n"
            "cd $REPO\n"
            "New-Item README.md -ItemType file | Out-Null\n"
            "git add README.md\n"
            '$Env:GIT_AUTHOR_DATE="2020-01-01T12:00:00"\n'
            '$Env:GIT_COMMITTER_DATE="2020-01-01T12:00:00"\n'
            'git commit --allow-empty -m "recreating contributions" | Out-Null\n'
            '$Env:GIT_AUTHOR_DATE="2020-01-01T12:00:00"\n'
            '$Env:GIT_COMMITTER_DATE="2020-01-01T12:00:00"\n'
            'git commit --allow-empty -m "recreating contributions" | Out-Null\n'
            '$Env:GIT_AUTHOR_DATE="2020-01-03T12:00:00"\n'
            '$Env:GIT_COMMITTER_DATE="2020-01-03T12:00:00"\n'
            'git commit --allow-empty -m "recreating contributions" | Out-Null\n'
            "\n"
            "git branch -M main\n"
            "git remote add origin git@github.com:fakeuser/$REPO.git\n"
            "git pull origin main\n"
            "git push -u origin main\n",
        ),
    ],
)
def test_fake_it(shell, expected):
    test_date1 = datetime.date(2020, 1, 1)
    test_date2 = datetime.date(2020, 1, 2)
    test_date3 = datetime.date(2020, 1, 3)
    res = recreate.fake_it(
        [(test_date1, 2), (test_date2, 0), (test_date3, 1)],
        "fakeuser",
        "testrepo",
        shell,
    )
    assert res == expected


def test_get_contrib_dates_from_query_res():
    QUERY_RESULT = {
        "data": {
            "user": {
                "contributionsCollection": {
                    "contributionCalendar": {
                        "totalContributions": 53,
                        "weeks": [
                            {
                                "contributionDays": [
                                    {"date": "2013-04-01", "contributionCount": 0},
                                    {"date": "2013-04-02", "contributionCount": 0},
                                    {"date": "2013-04-03", "contributionCount": 1},
                                    {"date": "2013-04-04", "contributionCount": 5},
                                    {"date": "2013-04-05", "contributionCount": 0},
                                    {"date": "2013-04-06", "contributionCount": 0},
                                ]
                            },
                            {
                                "contributionDays": [
                                    {"date": "2013-04-07", "contributionCount": 13},
                                    {"date": "2013-04-08", "contributionCount": 15},
                                    {"date": "2013-04-09", "contributionCount": 10},
                                    {"date": "2013-04-10", "contributionCount": 9},
                                ]
                            },
                        ],
                    }
                }
            }
        }
    }
    expected_result = [
        (datetime.date(2013, 4, 1), 0),
        (datetime.date(2013, 4, 2), 0),
        (datetime.date(2013, 4, 3), 1),
        (datetime.date(2013, 4, 4), 5),
        (datetime.date(2013, 4, 5), 0),
        (datetime.date(2013, 4, 6), 0),
        (datetime.date(2013, 4, 7), 13),
        (datetime.date(2013, 4, 8), 15),
        (datetime.date(2013, 4, 9), 10),
        (datetime.date(2013, 4, 10), 9),
    ]
    res = recreate.get_contrib_dates_from_query_res(QUERY_RESULT)
    assert list(res) == expected_result
