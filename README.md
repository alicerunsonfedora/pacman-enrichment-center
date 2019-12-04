# Pacman Enrichment Center

The Pacman Enrichment Center (PEC) is a tool to run tests against a set of agents designed for UC Berkeley's Pacman [Capture the Flag game](http://ai.berkeley.edu/contest.html). It offers similar functionality to their auto-grading system with a few features:

- Test cases written in JSON
- Arguments to run a specific test
- Option for CI-based tests (with exit codes)

## Running tests

To run a test with PEC, simply drop `autotest.py` and the `test_cases` folder into the Capture the Flag contest directory and run the following:

```
python autotest.py default
```