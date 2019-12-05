# Pacman Enrichment Center

The Pacman Enrichment Center (PEC) is a tool written in Python 3 to run tests against a set of agents designed for UC Berkeley's Pacman [Capture the Flag game](http://ai.berkeley.edu/contest.html). It offers similar functionality to their auto-grading system with a few features:

- Test cases written in JSON
- Arguments to run a specific test
- Option for CI-based tests (with exit codes)

## Running tests

To run a test with the PEC, simply drop `autotest.py`, `enrichment` folder, and the `test_cases` folder into the Capture the Flag contest directory and run the following:

```
python autotest.py default
```

`default` can be replaced with the name of the test case to run if the JSON file exists and [contains all of the proper parameters](#custom-test-configurations). For commands that involve generating custom checks, use `default`, though running the test is unnecessary.

### Optional runtime parameters:

- `--disable-exit-clause`: Disable the exit protocol at the end of the test. This is useful for environments that don't use the exit code.
- `--generate-custom-checks GENERATE_CUSTOM_CHECKS`: Write a custom check yourself that can be imported.
- `--custom CUSTOM`: The Python file name linking to a custom module.
- `--verbose`: Retain the output produced by capture.py.

## Custom test configurations

To write a custom test, create a JSON file in the `test_cases` directory.

### Required keys

- `iterations`: How many games to play over.
- `checks`: The list of checks to pass.
- `team`: A dictionary containing who's on the red/blue teams, or `"random"` if the tests should randomly assign it.

### Optional keys
- `allow_ties`: Whether ties should counted as passes in checks.
- `tolerance`: How many tests should be admitted before reporting a failure.
- `print_avg_score`: Whether to print the average game score.

### Example configuration
```json
{
    "iterations": 30,
    "checks": ["average_over_zero"],
    "team": {
      "red": "baselineTeam",
      "blue": "myTeam"
    },
    "tolerance": 0,
    "print_avg_score": false,
    "allow_ties": true
}
```

## Test checks

Most of the PEC works around the central idea of checks, similar to a continuous integration system. After running the games, checks will read the results and analyze them accordingly.

By default, there are three checks included in `TestCase`:

- `all_games_won`: Whether the team `myTeam` has won all games.
- `average_over_zero`: Whether the average score of all games is over zero.
- `majority_win`: Whether the team `myTeam` has won more games and it lost.

### Custom checks

The PEC supports writing custom checks out of the box and importing them, if necessary. To create a custom check, run the PEC with the `--generate-custom-checks` flag and then pass in the name of the check you want to create. For example, to create a check file called `custom_defeated_celestia.py`:

```
python autotest.py default --generate-custom-checks defeated_celestia
```

The following will create a new file with the following contents:

```python
# custom_defeated_celestia.py
# =========
# Written by autotest.py
# To import this into autotest, pass the custom flag and the
# name of the file.

from autotest import TestCase

class ImportedCases(TestCase):
    
    @TestCase.check(datafield='defeated_celestia', title="", passed="")
    def defeated_celestia(self):
        # Write your check here and have this check return a boolean
        # value.
        return False
```

From here, you can write a custom check by reading the test case's `data` and `results` as attributes of the `TestCase` class. You can also write more checks in here and reference them in your test cases.

To import a custom check file into the PEC, run the PEC with the `--custom` flag and the name of the Python file. For example, for the previous check we created:

```
python autotest.py default --custom custom_defeated_celestia.py
```

The PEC will copy the checks from the custom check you generated into the test case and run them as regular checks in that `TestCase` class.

### Decorated Check Functions

Checks should be decorated with the `@TestCase.check` decorator. It accepts the following parameters:

- `datafield`: (Required) The key to write into the test results.
- `title`: The title of the check as displayed when running the tests.
- `passed`: The text for when the check passes.
- `failed`: The test for when the check fails.

### Result Dictionary

All test results will include the following attributes in the `results` dictionary:

- `tests`: A list of boolean values indicating whether `myTeam` won that game.
- `avg_score`: The average score of all of the games.
- `passed_tests`: How many games `myTeam` won.
- `failed_tests`: How many games `myTeam` lost.


## Use with GitHub Actions

One can write a custom workflow like the one below to use PEC as a CI test:

```yml
name: Test
on: push

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        test-cases:
          - 'severe'
          - 'bestof100'
      fail-fast: false
    steps:
      - name: Checkout source code
        uses: actions/checkout@v1
      - name: Setup Python
        uses: actions/setup-python@v1
        with:
          python-version: '3.7'
          architecture: 'x64'
      - name: Run ${{ matrix.test-cases }} test
        run: python autotest.py $testcase
        env:
          testcase: ${{ matrix.test-cases }}
```