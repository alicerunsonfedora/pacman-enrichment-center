# Pacman Enrichment Center
# test_case.py
# ========================
# (C) 2019 Marquis Kurt.
# Licensed under Non-violent Public License v1.
from random import choice
from functools import reduce
from os import listdir
from json import load
import capture
import types

class TestCase():
    """
        Base class for running a test case. Handles importing JSON data, running checks,
        and importing test modules.
    """

    data = {}
    "The test case properties. This is usually loaded in by a JSON file."
    
    results = {}
    "The results of the test case. Usually includes avg_score, tests, passed_tests, and failed_tests"

    verbose: bool = False
    "Whether capture.py's output will be retained during run."

    def check(datafield: str, title: str = "Check", passed: str = "Check passed!",
              failed: str = "Check failed."):
        """
            Write a check for a test case. This is used as a decorator for instance methods
            to make writing checks easier at runtime. The check function itself should be a 
            function that returns a boolean value.

            :param datafield: The key to write into the test results.
            :param title: (Optional) The title of the check to be displayed.
            :param passed: (Optional) The text for when the check passes.
            :param failed: (Optional) The text for when the check fails.
            :returns: A decorated function for use in a test case.
        """
        def check_decorator(func):
            def run_check(self):
                self.results[datafield] = func(self)
                print("\n" + title)
                if self.results[datafield]:
                    print("\033[32;1m✔️ %s\033[0m" % (passed,))
                else:
                    print("\033[31;1m⨯ %s\033[0m" % (failed,))
                return self.results[datafield]
            return run_check
        return check_decorator

    def __run_iterations__(self):
        """
            Run a series of tests by looking at the test data.
        """

        score = 0
        tests = []
        for i in range(self.data['iterations']):
            red, blue = self.generate_team()
            capture_args = capture.readCommand([
                "-Q", "-l", "RANDOM", "-r", red, "-b", blue
            ])
            game = capture.runGames(**capture_args)
            game_score = game[0].state.data.score

            score += game_score if game_score > 0 else -1 * game_score

            allow_ties = self.data['allow_ties'] if "allow_ties" in self.data.keys(
            ) else False

            if red == "myTeam":
                tests.append(score >= 0 if allow_ties else score > 0)
            else:
                tests.append(score <= 0 if allow_ties else score < 0)

        score /= self.data['iterations']

        self.results['tests'] = tests
        self.results['avg_score'] = score
        self.results['passed_tests'] = tests.count(True)
        self.results['failed_tests'] = tests.count(False)

    @check(datafield="all_games_won", title="Won All Games", passed="All games won!")
    def all_games_won(self):
        """
            Check that determines whether or not the team has won all games.
            This may include ties and a fail tolerance if described in the 
            test case data.
        """
        if "tests" in self.results.keys():
            def add_bool(arg1, arg2): return arg1 and arg2
            won_all_games_list = self.results['tests'].copy()

            if "tolerance" in self.data.keys():
                if self.data['tolerance'] > 0:
                    tcount = 0
                    while tcount < self.data['tolerance'] + 1:
                        if False in won_all_games_list:
                            won_all_games_list.remove(False)
                        tcount += 1

            if won_all_games_list:
                return reduce(add_bool, won_all_games_list)
        else:
            return False

    @check(datafield="average_over_zero", title="Game Average Score", passed="Game average score over zero!")
    def average_over_zero(self):
        """
            Check that determines whether the team's average score is over zero points.
        """
        return self.results['avg_score'] > 0

    @check(datafield='majority_win', title="Majority Win", passed="Won more games than lost!")
    def majority_win(self):
        """
            Check that determines whether the team won more games than lost.
        """
        return self.results['passed_tests'] > self.results['failed_tests']

    def generate_team(self):
        """
            Generate a tuple containing a random assignment of teams.
        """
        choices = [("myTeam", "baselineTeam"), ("baselineTeam", "myTeam")]

        if self.data['team'] == "random":
            return choice(choices)
        else:
            return self.data['team']['red'], self.data['team']['blue']

    def get_JSON_data(self, name: str):
        """
            Load a JSON into the test data.
        """
        json_path = "test_cases/" + name + ".json"
        with open(json_path, 'r') as json_file_data:
            json: dict = load(json_file_data)
        return json

    def exists(self, name: str):
        """
            Determine whether the test case exists in the test cases directory.
        """
        tests = listdir("./test_cases")
        return name + ".json" in tests

    def is_compliant(self, name: str):
        """
            Check whether the test case is a valid test case.
        """
        if self.exists(name):
            json_path = "test_cases/" + name + ".json"
            with open(json_path, 'r') as json_file_data:
                json: dict = load(json_file_data)

                required_keys = ["iterations", "checks", "team"]
                current_keys = list(json.keys())

                for key in required_keys:
                    if key not in current_keys:
                        return False

                optional_keys = ["tolerance", "print_avg_score", "allow_ties"]

                if "allow_ties" in current_keys:
                    if type(json['allow_ties']) is not bool:
                        return False

                if "tolerance" in current_keys:
                    if type(json['tolerance']) is not int:
                        return False

                if "print_avg_score" in current_keys:
                    if type(json['print_avg_score']) is not bool:
                        return False

            return True
        else:
            return False

    def load(self, name: str):
        """
            Load a compliant JSON file as test data.
            :param name: The name of the test
        """
        if self.is_compliant(name):
            self.data = self.get_JSON_data(name)
        else:
            raise ValueError("JSON file is not valid or malformed.")

    def inject_custom(self, checks: object):
        """
            Copy test cases from an object into the currently-loaded test case.

            :param checks: The object to copy test cases from.
        """
        for attribute in checks.__dict__.keys():
            if not hasattr(self, attribute):
                try:
                    self.__dict__[attribute] = types.MethodType(checks.__dict__[attribute], self)
                    print("Imported check %s." % (attribute))
                except:
                    pass
                
        
    def run(self):
        """
            Run the tests and checks.
        """
        checks: list = self.data['checks']
        self.__run_iterations__()

        allow_ties = self.data["allow_ties"] if "allow_ties" in self.data.keys(
        ) else False

        if not self.verbose:
            print("\0332J")

        print("\033[1mTest Results\033[0m")
        print("Total Iterations: %s" % (self.data['iterations'],))
        print("Games won%s: %s" %
              (' (or tied)' if allow_ties else '', self.results['passed_tests'],))
        print("Games lost: %s" % (self.results['failed_tests'],))

        if "print_avg_score" in self.data.keys():
            if self.data['print_avg_score']:
                print("Average score: %s" % (self.results['avg_score'],))

        print("\n\033[1mChecks\033[0m (%s total)" % (len(checks),))
        check_tests = []

        for check in checks:
            if hasattr(self, "%s" % (check,)):
                check_tests.append(eval("self.%s()" % (check,)))
            else:
                print(
                    "\033[33;1m⚠️ Check '%s' does not exist. Skipping. \033[0m" % (check,))

        if check_tests.count(False) > 0:
            print("\n\033[31;1m⨯ %s check%s have failed.\033[0m" % (
                check_tests.count(False), 's' if check_tests.count(False) > 1 else ''))
            return 2
        else:
            print("\033[32;1m✔️ All checks passed!\033[0m")
            return 0
