#No additional libaries are needed to use this file
#Done by Chong Li Heng 2603072

import subprocess
import sys
import json

#function to key in the inputs into main.py and check if expected output matches actual output
def tester(testcasename, user_inputs,expected_output):
    #types the inputs into the terminal
    format_input = "\n".join(str(inputs) for inputs in user_inputs) + "\n"
    process = subprocess.run(
        [sys.executable, "main.py"],
        input = format_input,
        capture_output = True,
        text = True
    )

    #checks if the output matches expected outputs
    if expected_output in process.stdout:
        print(f"""\n{testcasename} test case passed\n""")
    else:
        print(f"""
{testcasename} Failed: 
Expected Output: {expected_output}
Actual Output: {process.stdout}
""")


with open("testcase.json",'r') as file:
    test_case_list = json.load(file)


#runs the test cases
for test_case in test_case_list:
    testcasename = test_case['Test Case Name']
    input = test_case['Inputs']
    expected_output = test_case["Expected_Output"]
    tester(testcasename,input,expected_output)

print("\nTest has ended")