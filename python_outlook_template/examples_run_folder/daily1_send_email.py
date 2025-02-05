# Created by: Michael Johnson - 11-21-2024
# Helper script to take in variables and prepare eamil using 'outlook_mac_email'

# https://stackoverflow[.]com/questions/61529817/automate-outlook-on-mac-with-python
# https://stackoverflow[.]com/users/6278428/jayme-gordon
# Seems to work with just appscript import (mactypes included in PiPI install of appscript) , but noted as unmaintained

# Import primary script functions
import outlook_mac_email as emaillib
# Import json to easily parse vars
import json
# Import date and time to autofill
from datetime import date

with open('daily1_vars.json', 'r') as vars_file:
    variable_names = json.load(vars_file)

with open(variable_names["in_file_name"], 'r') as body_file:
    body = body_file.read()

today_var = date.today()
email_date = today_var.strftime("%m/%d/%y")

dynamic_subject = variable_names["subject_vars"]["case"] + " " + variable_names["subject_vars"]["client_name"] + " " + email_date + " " + variable_names["subject_vars"]["title"]
create_draft_email = emaillib.Message(subject=dynamic_subject, body=body, to_recip=variable_names["to_recip"], cc_recip=variable_names["cc_recip"], bcc_recip=variable_names["bcc_recip"])
