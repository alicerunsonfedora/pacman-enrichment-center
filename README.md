# Pacman Enrichment Center

The Pacman Enrichment Center (PEC) is a tool written in Python 3 to run tests against a set of agents designed for UC Berkeley's Pacman [Capture the Flag game](http://ai.berkeley.edu/contest.html). It offers similar functionality to their auto-grading system with a few features:

- Test cases written in JSON
- Arguments to run a specific test
- Option for CI-based tests (with exit codes)

## Running tests

To run a test with PEC, simply drop `autotest.py` and the `test_cases` folder into the Capture the Flag contest directory and run the following:

```
python autotest.py default
```

### Optional runtime parameters:

- `--disable-exit-clause`: Disable the exit protocol at the end of the test. This is useful for environments that don't use the exit code.

## Custom test configurations

To write a custom test, create a JSON file in the `test_cases` directory.

### Required keys

- `all_tests_pass`: Whether the test should verify that all of the tests pass
- `watch_score`: Whether the test should keep track of the average score and present it in the test results
- `iterations`: The number of tests to run.

### Optional keys

- `team`: A dictionary that defines the red and blue teams. Defaults to a random config.
- `tolerance`: How many failed tests can be considered admissible. Defaults to `0`

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