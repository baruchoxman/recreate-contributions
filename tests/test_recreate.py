import recreate
import datetime
import pytest


@pytest.mark.parametrize(
    "shell,expected",
    [
        (
            "bash",
            "GIT_AUTHOR_DATE=2020-01-01T12:00:00 "
            "GIT_COMMITTER_DATE=2020-01-01T12:00:00 "
            "git commit --allow-empty -m "
            '"recreating contributions" > /dev/null\n',
        ),
        (
            "powershell",
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
            "bash",
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
            "powershell",
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
