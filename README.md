# Recreate Contributions

[![GitHub Actions](https://github.com/baruchoxman/recreate-contributions/actions/workflows/test.yml/badge.svg)](https://github.com/baruchoxman/recreate-contributions/actions)
[![GitHub Actions](https://codecov.io/gh/baruchoxman/recreate-contributions/branch/main/graph/badge.svg)](https://codecov.io/gh/baruchoxman/recreate-contributions)
[![pre-commit.ci status](https://results.pre-commit.ci/badge/github/baruchoxman/recreate-contributions/main.svg)](https://results.pre-commit.ci/latest/github/baruchoxman/recreate-contributions/main)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black")

### Description

This is a tool that helps to replicate the contribution history from one GitHub user into another.
For more information please see [this link from GitHub](https://docs.github.com/en/account-and-profile/setting-up-and-managing-your-github-profile/managing-contribution-graphs-on-your-profile).
This is done by creating a new github private repository and recreating the commits distribution from source user's history into the new repository.
Contributions breakdown, such as pull requests, issues activity and code review activity will be lost, and will be represented through commits as well.

This project has been inspired by and based on the [gitfiti](https://github.com/gelstudios/gitfiti) project.

### Usage

```shell
usage: recreate.py [-h] -u USERNAME -s SOURCE -d DATE -t APITOKEN [-r REPO]

Recreate contributions

optional arguments:
  -h, --help            show this help message and exit
  -u USERNAME, --username USERNAME
                        GitHub username to update
  -s SOURCE, --source SOURCE
                        Source GitHub username to copy contributions from
  -d DATE, --date DATE  Start date for copying contributions (YYYY-MM-DD)
  -t APITOKEN, --apitoken APITOKEN
                        API token for github (create at https://github.com/settings/tokens)
  -r REPO, --repo REPO  Repository to use (will use "contrib-copy-<source username>" if not provided
```

### Example

```shell
python ./recreate.py -u my-username -s my-old-username -d 2020-01-01 -t "<token from GitHub>"
```

### License

This project is released under [The MIT license (MIT)](http://opensource.org/licenses/MIT)

### TODO

- Support replicating pull requests, issues and code reviews, to preserve the contributions distribution between categories.
