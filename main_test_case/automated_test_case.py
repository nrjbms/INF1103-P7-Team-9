#No additional libaries are needed to use this file
#Done by Chong Li Heng 2603072

import subprocess
import sys
import json
import os

# Folder this script lives in (main_test_case/) and the repo root (one level up)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(BASE_DIR)

JSON_PATH = os.path.join(BASE_DIR, "testcase.json")
APP_PATH = os.path.join(ROOT_DIR, "justeat.py")

#function to key in the inputs into justeat.py and check if expected output matches actual output
def tester(testcasename, user_inputs, expected_output):
    #types the inputs into the terminal
    format_input = "\n".join(str(i) for i in user_inputs) + "\n"
    try:
        process = subprocess.run(
            [sys.executable, APP_PATH],
            input=format_input,
            capture_output=True,
            text=True,
            cwd=ROOT_DIR,      # run from repo root so justeat.py finds its own files
            timeout=30         # stops CI hanging if the program waits for more input
        )
    except subprocess.TimeoutExpired:
        print(f"\n{testcasename} Failed: program timed out\n")
        return False

    #checks if the output matches expected outputs
    if expected_output in process.stdout:
        print(f"\n{testcasename} test case passed\n")
        return True
    else:
        print(f"""
{testcasename} Failed:
Expected Output: {expected_output}
Actual Output: {process.stdout}
Errors: {process.stderr}
""")
        return False


with open(JSON_PATH, 'r') as file:
    test_case_list = json.load(file)

#runs the test cases
failed = 0
for test_case in test_case_list:
    testcasename = test_case['Test Case Name']
    inputs = test_case['Inputs']
    expected_output = test_case["Expected_Output"]
    if not tester(testcasename, inputs, expected_output):
        failed += 1

print(f"\nTest has ended: {len(test_case_list) - failed} passed, {failed} failed")

#makes GitHub Actions go red if any test failed
if failed > 0:
    sys.exit(1)