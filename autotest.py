# Pacman Enrichment Center
# autotest.py
# ========================
# (C) 2019 Marquis Kurt.
# Licensed under Non-violent Public License v1.

from enrichment import TestCase
import importlib
import argparse
import sys

def generate_custom_checks(name: str):
    """
        Write a custom check file used for import.

        :param name: The name of the check to create.
    """
    with open('custom_%s.py' % (name), 'w+') as custom:
        custom.write("""
# custom_%s.py
# =========
# Written by autotest.py
# To import this into autotest, pass the custom flag and the
# name of the file.

from autotest import TestCase

class ImportedCases(TestCase):
    
    @TestCase.check(datafield='%s', title="", passed="")
    def %s(self):
        # Write your check here and have this check return a boolean
        # value.
        return False
        """ % (name, name, name))

def initialize_arguments():
    """
        Run through an argument parser and determine what actions to take.
    """
    parser = argparse.ArgumentParser(
        description="Run tests on agents in capture.py with ease.")
    parser.add_argument(
        "test", help="The name of the test to run, or all tests.")
    parser.add_argument('--disable-exit-clause', nargs='?',
                        help="Do not return an exit code when running tests.")
    parser.add_argument('--custom', help="Add additional checks from a file into the test system.")
    parser.add_argument('--generate-custom-checks', help="Generate a custom check case suitable for import.")
    parser.add_argument('--verbose', '-v', help="Retain the output produced from capture.py.")
    return parser.parse_args()


if __name__ == "__main__":
    prog_args = initialize_arguments()
    mainCase = TestCase()

    if prog_args.verbose is not None:
        mainCase.verbose = prog_args.verbose

    if prog_args.custom is not None:
        print("Requested custom checks. Finding module...")
        import_name: str = prog_args.custom 
        import_name = import_name.replace(".py", "")
        import_module = None
        
        try:
            import_module = importlib.import_module(import_name)
        except:
            print("Module %s not found. Aborting import..." % (import_name))

        if import_module is not None:
            print("Importing test cases from module...")
            try:
                custom_checks = getattr(import_module, "ImportedCases")
                mainCase.inject_custom(custom_checks)
            except:
                print("Couldn't import ImportedCases class from module. Aborting import...")

    if prog_args.generate_custom_checks is not None:
        generate_custom_checks(prog_args.generate_custom_checks)
        sys.exit(0)

    try:
        print("Running test '%s'..." % (prog_args.test))
        mainCase.load(prog_args.test)
    except:
        print("Test case %s is missing or malformed. Aborting." %
              (prog_args.test,))

        if prog_args.disable_exit_clause is None:
            sys.exit(1)

    exit_code = mainCase.run()
    if prog_args.disable_exit_clause is None:
        sys.exit(exit_code)
