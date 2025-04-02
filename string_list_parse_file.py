# Michael Johnson - Feb 2024
# Simple Python Script to convert from lines of lists to just string text (seperated by lines of values from lists)
# WARNING: Currently assume each line is only 1 item in list

import sys
import ast

# Expects full file string upon script launch in shell (CLI)
# Example1 ">string_list_parse.py /user/someuser/home/folder/text_test.txt"
# Example2 ">python3 string_list_parse.py /user/someuser/home/folder/text_test.txt"
# Example3 ">string_list_parse.py ./text_test.txt"
# Example4 ">string_list_parse.py text_test.txt"
full_file_string = (sys.argv[1])

working_string = ""

# with open('./text_test.txt', 'r') as file:
with open(full_file_string, 'r') as file:
    lines_of_file = file.readlines()

    for list in lines_of_file:
        list_value = ast.literal_eval(list)
        working_string += list_value[0]
        working_string += "\n"

    print(working_string)

    file.close()

with open('./python_output.txt', 'w') as file2:
    file2.write(working_string)

    file2.close()
