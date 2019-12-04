# autotest.py
# ===========
# An automatic test service for capture.py
# (C) 2019 Marquis Kurt.
# Inspired by Ben Rock's original script

from random import choice
from functools import reduce
from sys import argv
from os import listdir
from json import load
import capture
import sys

def display_help():
    print("""\
Pacman Enrichment Center
v1.0.2

Paramaters:
--no-exit-clause - Do not return an exit code when running tests

Required:
The name of the test should be specified as the first argument.

Example:
autotest.py severe
    """)

def select_team():
    """
        Generate a random team tuple.

        :returns: A tuple containing the red team and blue team
    """

    choices = [("myTeam", "baselineTeam"), ("baselineTeam", "myTeam")]

    return choice(choices)

def run_tests(track_score: bool = False, 
                all_tests_pass: bool = True, 
                iterations: int = 10, 
                fail_tolerance: int = 0, 
                team: (str, str) = None,
                allow_ties: bool = False):
    """
        Run a series of tests on capture.py given some parameters.

        :param track_score: Whether the tests should track the score. Defaults to False.
        :param all_tests_pass: Whether to verify that all of the tests pass. Defaults to True.
        :param iterations: How many games to run for evaluation. Defaults to 10.
        :param fail_tolerance: How many times the tests can fail before being marked as a failure. Defaults to 0.
        :param team: The specified team configuration, if necessary. Defaults to None.
        :param allow_ties: Whether ties should be counted as successes.
        :returns: A dictionary containing the requested information.
    """
    sum = 0
    test_cases = []

    for i in range(iterations):
        red, blue = team if team is not None else select_team()
        simulated_args = capture.readCommand([
            "-Q", "-l", "RANDOM", "-r", red, "-b", blue
        ])
        game = capture.runGames(**simulated_args)
        score = game[0].state.data.score

        sum += score

        if red == "myTeam":
            test_cases.append(score >= 0 if allow_ties else score > 0)
        else:
            test_cases.append(score <= 0 if allow_ties else score < 0)
    
    sum /= iterations
    and_func = lambda arg1, arg2: arg1 and arg2

    if fail_tolerance > 0:
        tolerance_counter = 0
        while tolerance_counter < fail_tolerance + 1:
            if False in test_cases:
                test_cases.remove(False)
            tolerance_counter += 1


    if test_cases:
        passed_tests = reduce(and_func, test_cases)

    test_results = {}

    if track_score:
        test_results['avg_score'] = sum

    if all_tests_pass:
        test_results['passes_tests'] = passed_tests

    test_results['tests'] = test_cases
    test_results['iterations'] = iterations
    test_results['tolerance'] = fail_tolerance

    return test_results

def find_test_case(name: str):
    """
        Check whether the test case is listed in the test cases folder.
        :param name: The name of the test case.
    """
    tests = listdir("./test_cases")
    return name + ".json" in tests

def get_test_params(name: str):
    """
        Get the test parameters from a test case.
        :param name: The name of the test case. Should point to a JSON file.
        :returns: A tuple containing the params for the test cases.
        :raises: ValueError if the JSON is malformed.
    """
    watch_score = False
    all_tests_pass = True
    iterations = 10
    fail_tolerance = 0
    team = None
    ties = False
    
    if find_test_case(name):
        json_path = "test_cases/" + name + ".json"
        with open(json_path, 'r') as json_file:
            json_data = load(json_file)
            
            required_keys = ["watch_score", "all_tests_pass", "iterations"]
            json_keys = list(json_data.keys())
            
            for key in required_keys:
                if key not in json_keys:
                    raise ValueError("JSON file malformed. Missing key: %s" % (key))

            watch_score = json_data["watch_score"]
            all_tests_pass = json_data["all_tests_pass"]
            iterations = json_data["iterations"]

            if "allow_ties" in json_keys:
                ties = json_data["allow_ties"]

            if "tolerance" in json_keys:
                fail_tolerance = json_data["tolerance"]

            if "team" in json_keys:
                t = json_data["team"]

                team_keys = t.keys()
                if "red" not in team_keys or "blue" not in team_keys:
                    raise ValueError("JSON file malformed. Missing team keys")

                team = t["red"], t["blue"]
    
    return (watch_score, all_tests_pass, iterations, fail_tolerance, team, ties)

if __name__ == "__main__":
    """
        Run a test case. The only argument to be passed in is the name of the test case.
        Test cases default to "default", pointing to "test_cases/default.json".
    """

    test_case = "default"
    args = argv[1:]

    if not args:
        display_help()
    else:
        if args and not args[0].startswith("--"):
            test_case = args[0]
        exit_code = 0
        disable_exit_check = "--no-exit-clause" in args
        
        score, all_pass, iteration, tolerance, team, ties = get_test_params(test_case)

        print("Running tests from %s.json..." % (test_case))
        if team is not None:
            print("Team configuration: %s" % (team,))
        results = run_tests(track_score=score, 
                            all_tests_pass=all_pass, 
                            iterations=iteration, 
                            fail_tolerance=tolerance,
                            team=team,
                            allow_ties=ties)

        print("\n\nTEST RESULTS")
        print("Ran the tests over %s iterations." % (iteration))

        if score:
            print("Average score was: %s points" % (results['avg_score']))

        if all_pass:
            if tolerance > 0:
                print("Note: Fail tolerance set to a max of %s tests." % (tolerance))
            passed = results['passes_tests']
            if passed:
                print("All tests PASSED!")
            else:
                print("All tests FAILED!")
                exit_code = 2
        
        print("Note: These tests may not reflect your actual grade. Consult your instructor for details.")
        
        if not disable_exit_check:
            sys.exit(exit_code)
