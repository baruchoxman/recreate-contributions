import datetime
from typing import Any, Dict, List

import pytest
import responses

import recreate


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
def test_commit(shell: recreate.Shells, expected: str) -> None:
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
def test_fake_it(shell: recreate.Shells, expected: str) -> None:
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


def test_get_contrib_dates_from_query_res() -> None:
    query_result = _get_query_result_mock(datetime.date(2013, 4, 1), 10)
    expected_result = [
        (datetime.date(2013, 4, 1), 0),
        (datetime.date(2013, 4, 2), 1),
        (datetime.date(2013, 4, 3), 2),
        (datetime.date(2013, 4, 4), 3),
        (datetime.date(2013, 4, 5), 4),
        (datetime.date(2013, 4, 6), 5),
        (datetime.date(2013, 4, 7), 6),
        (datetime.date(2013, 4, 8), 7),
        (datetime.date(2013, 4, 9), 8),
        (datetime.date(2013, 4, 10), 9),
    ]
    res = recreate.get_contrib_dates_from_query_res(query_result)
    assert list(res) == expected_result


@responses.activate
def test_get_all_contrib_dates_start_after_end_date() -> None:
    today = datetime.date.today()
    res = recreate.get_all_contib_dates(
        "dummy",
        today + datetime.timedelta(days=1),
        today,
        "dummy_key",
    )
    assert not res
    assert not responses.calls


@responses.activate
def test_get_all_contrib_dates_same_start_and_end_date() -> None:
    test_date = datetime.date(2020, 1, 1)
    query_result = _get_query_result_mock(test_date, 1)
    responses.add(responses.POST, recreate.QUERY_API_URL, status=200, json=query_result)
    res = recreate.get_all_contib_dates("dummy", test_date, test_date, "dummy_key")
    assert res == [(test_date, 0)]
    assert len(responses.calls) == 1


@responses.activate
def test_get_all_contrib_dates_one_chunk() -> None:
    test_date = datetime.date(2020, 1, 1)
    query_result = _get_query_result_mock(
        test_date,
        recreate.CONTRIB_DATES_DELTA_IN_DAYS,
    )
    responses.add(responses.POST, recreate.QUERY_API_URL, status=200, json=query_result)

    res = recreate.get_all_contib_dates(
        "dummy",
        test_date,
        test_date + datetime.timedelta(recreate.CONTRIB_DATES_DELTA_IN_DAYS - 1),
        "dummy_key",
    )
    assert len(res) == recreate.CONTRIB_DATES_DELTA_IN_DAYS
    assert len(responses.calls) == 1


@responses.activate
def test_get_all_contrib_dates_two_chunks() -> None:
    test_date = datetime.date(2020, 1, 1)
    query_result1 = _get_query_result_mock(
        test_date,
        recreate.CONTRIB_DATES_DELTA_IN_DAYS,
    )
    query_result2 = _get_query_result_mock(
        test_date + datetime.timedelta(recreate.CONTRIB_DATES_DELTA_IN_DAYS),
        5,
    )
    responses.add(
        responses.POST,
        recreate.QUERY_API_URL,
        status=200,
        json=query_result1,
    )
    responses.add(
        responses.POST,
        recreate.QUERY_API_URL,
        status=200,
        json=query_result2,
    )
    res = recreate.get_all_contib_dates(
        "dummy",
        test_date,
        test_date + datetime.timedelta(recreate.CONTRIB_DATES_DELTA_IN_DAYS + 5),
        "dummy_key",
    )
    assert len(res) == recreate.CONTRIB_DATES_DELTA_IN_DAYS + 5
    assert len(responses.calls) == 2


@responses.activate
def test_get_all_contrib_dates_with_exception() -> None:
    test_date = datetime.date.today()
    responses.add(responses.POST, recreate.QUERY_API_URL, status=401, json={})
    with pytest.raises(Exception) as exc_info:
        recreate.get_all_contib_dates(
            "dummy",
            test_date,
            test_date,
            "dummy_key",
        )
    assert str(exc_info.value).startswith(
        "Query failed to run by returning code of 401.",
    )
    assert len(responses.calls) == 1


def _get_query_result_mock(start_date: datetime.date, num_of_dates: int) -> Any:
    return {
        "data": {
            "user": {
                "contributionsCollection": {
                    "contributionCalendar": {
                        "totalContributions": num_of_dates * (num_of_dates - 1) / 2,
                        "weeks": _get_weeks(start_date, num_of_dates),
                    },
                },
            },
        },
    }


def _get_weeks(
    start_date: datetime.date,
    num_of_dates: int,
) -> List[Dict[str, List[Dict[str, Any]]]]:
    weeks = []

    for week in range(0, num_of_dates // 7 + 1):
        days = []
        for day in range(0, min(num_of_dates - 7 * week, 7)):
            day_num = week * 7 + day
            days.append(
                {
                    "date": (start_date + datetime.timedelta(days=day_num)).isoformat(),
                    "contributionCount": day_num,
                },
            )
        weeks.append({"contributionDays": days})

    return weeks


def test_parse_args() -> None:
    args = [
        "-u",
        "testuser",
        "-s",
        "sourceuser",
        "-d",
        "2022-01-20",
        "--apitoken",
        "<token>",
    ]
    parsed_args = recreate.parse_args(args)
    assert parsed_args.username == "testuser"
    assert parsed_args.source == "sourceuser"
    assert parsed_args.date == datetime.date(2022, 1, 20)
    assert parsed_args.apitoken == "<token>"
    assert parsed_args.repo is None
