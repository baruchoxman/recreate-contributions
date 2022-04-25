import recreate
import datetime
import pytest


@pytest.mark.parametrize("shell,expected", [
    ("bash",
     "GIT_AUTHOR_DATE=2020-01-01T12:00:00 GIT_COMMITTER_DATE=2020-01-01T12:00:00 "
     "git commit --allow-empty -m \"recreating contributions\" > /dev/null\n"),
    ("powershell",
     "$Env:GIT_AUTHOR_DATE=\"2020-01-01T12:00:00\"\n"
     "$Env:GIT_COMMITTER_DATE=\"2020-01-01T12:00:00\"\n"
     "git commit --allow-empty -m \"recreating contributions\" | Out-Null\n"),
])
def test_commit(shell, expected):
    test_date = datetime.date(2020,1,1)
    res = recreate.commit(test_date, shell)
    assert res == expected
