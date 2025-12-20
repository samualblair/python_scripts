# Created by: Michael Johnson - 10-15-2025
# Scripts to upload QKview file(s) to iHealth, pull information for iHealth and customize report data

# import required modules
import os
import json
import time
# import sys
# import csv

# Requests option
import requests



def f5_ihealth_api_get_diagnostics_json(f5_ihealth_token:str, f5_ihealth_qkview_id:str) -> dict:
    """
    Logs into ihealth api , obtains diagnostics data in JSON format and returns as a dictionary
    """

    url = f"https://ihealth-api.f5.com/qkview-analyzer/api/qkviews/{f5_ihealth_qkview_id}/diagnostics.json?set=hit"

    headers = {
        'Accept': 'application/vnd.f5.ihealth.api',
        'Authorization': f'Bearer {f5_ihealth_token}'
    }

    # TODO: Identify proper CA cert for verification
    # response = requests.request("GET", url, headers=headers, verify=server_cert_ca_location)
    response = requests.request("GET", url, headers=headers)
    
    print(f"The response code was: {response.status_code}")
    # print(response.text)

    # To load response as object
    # json_dict = response.json
    # Then to print back as formatted string
    # json_string = json.dumps(json_dict, indent=4)
    return(response.json())


def f5_ihealth_api_login(f5_ihealth_user:str, f5_ihealth_pass:str, ca_cert:str) -> str:
    """
    Logs into ihealth api and returns token
    """

    # # Setup Session to include Basic Auth
    # session = requests.Session()
    # session.auth = (f5_ihealth_user, f5_ihealth_pass)

    # Random value? Account number? 
    # Seems to be a Static ID for the iHealth Open Auth 2 ID - ausp95ykc80HOU7SQ357
    # See https://clouddocs.f5.com/api/ihealth/Authentication.html
    ihealth_oauth2_app_id = "ausp95ykc80HOU7SQ357"

    url = f"https://identity.account.f5.com/oauth2/{ihealth_oauth2_app_id}/v1/token"
    payload = 'grant_type=client_credentials&scope=ihealth'

    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    # TODO: Identify proper CA cert for verification
    # response = requests.request(
    #     "POST", url, headers=headers, data=payload, verify=ca_cert, auth=(f5_ihealth_user, f5_ihealth_pass))
    
    response = requests.request(
        "POST", url, headers=headers, data=payload, auth=(f5_ihealth_user, f5_ihealth_pass))

    # TODO: Add Custom logic for highlighting expected errors or API rate limiting
    # if response.status_code == 429:
    #     print(f"Hitting Rate Limits due to response code was: {response.status_code}")
    #     print("Waiting 10 sec...")
    #     time.sleep(10)
    #     print("Continuing...and Trying Again")
    #     response = requests.request(
    #         "POST", url, headers=headers, data=payload, verify=server_cert_ca_location)

    # if response.status_code == 409:
    #     print(f"The Object Probably Already Existed - The response code was: {response.status_code}")
    # else:    
    #     print(f"The response code was: {response.status_code}")

    print(f"The response code was: {response.status_code}")

    # print(response.text)
    response_json = response.json()
    access_token = response_json["access_token"]

    # Arbitrary 1 second wait to ensure access token is in effect prior to other API calls
    time.sleep(1)

    return(access_token)


def upload_qkview_to_ihealth(f5_ihealth_token:str, qkview_file:str):
    """
    Uploads a QKview file to iHealth
    """

    # print(qkview_file)
    ihealth_visible_in_gui = ''
    ihealth_description = ''
    ihealth_f5_support_case = ''
    ihealth_share_with_case_owner = ''
    

    url = 'https://ihealth2-api.f5.com/qkview-analyzer/api/qkviews'
    payload = {
        'visible_in_gui': 'True',
        'description': 'api sending of qkview',
        'f5_support_case': '',
        'share_with_case_owner': ''
    }
    files=[
        ('qkview',('example.qkview',open('example.qkview','rb'),'application/octet-stream'))
    ]


    headers = {
        'Accept': 'application/vnd.f5.ihealth.api',
        'Authorization': f'Bearer {f5_ihealth_token}'
    }
    
    # TODO: Identify proper CA cert for veritication
    # response = requests.request(
    #     "POST", url, headers=headers, data=payload, verify=ca_cert)
    
    response = requests.request(
        "POST", url, headers=headers, data=payload)

    print(f"The response code was: {response.status_code}")

    # print(response.text)
    response_json = response.json()
    access_token = response_json["access_token"]

    # Arbitrary 1 second wait to ensure access token is in effect prior to other API calls
    time.sleep(1)

    return(access_token)


def upload_directory_files_to_ihealth(token, directory:str):
    """
    Recursively finds QKview files and uploads to iHealth
    """

    # iterate over files in
    # that directory
    # Walk directory tree and record for later use
    recursive_folder_list = []    
    for currentpath, folders, files in os.walk(directory):
        for folder in folders:
            # print(os.path.join(currentpath, file))
            recursive_folder_list.append(os.path.join(currentpath, folder))
    # Also add base folder to list
    recursive_folder_list.append(directory)

    # print(sys.argv[1])
    try:
        for folder_name in recursive_folder_list:
            for file_name in os.listdir(folder_name):
                file_contents = os.path.join(folder_name, file_name)
                # checking if it is a file
                if os.path.isfile(file_contents):
                    try:
                        # Only try to parse file if it is name ends with .json
                        if file_name[-7:] == ".qkview":
                            upload_qkview_to_ihealth(token, file_contents)
                    # Catch when file is not parsable UTF 8 or similar
                    except UnicodeDecodeError:
                        print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
    except IndexError:
        print('Issue with file - ' + file_name)


if __name__ == "__main__":

    ihealth_operation_chosen = input('Please enter your selection - Submit QKview to iHealth or Obtain report ( all , 1_submit , 2_report ) \n')

    # Assign base directory - For parsing QkView Files and storing reports
    base_directory = input('Please enter folder name to parse QKview files recursively and/or Store Reports in (HINT: may navigate back a folder with ../FOLDERNAME )\n')

    # USER CAN BE CREATED at https://account.f5.com/ihealth2 or https://account.f5.com/ihealth
    # Navigating to the settings page, and generating a Client ID and Client Secret by clicking the relevant button.

    user = input('Please enter iHealth API Username - This should be API Specific not normal Web Username \n')
    password = input('Please enter iHealth API Password - This should be API Specific not normal Web Username \n')
    server_cert_ca_location = input('Please enter CA location for iHealth\n')


    login_token = f5_ihealth_api_login(user,password,server_cert_ca_location)

    upload_directory_files_to_ihealth(login_token, base_directory)

    f5_ihealth_qkview_id_list = [
        "00000000",
        "00000001"
    ]


    for f5_ihealth_qkview_id in f5_ihealth_qkview_id_list:
        ihealth_diagnostic_data_dict = f5_ihealth_api_get_diagnostics_json(login_token, f5_ihealth_qkview_id)
        filename_string = f'./{ihealth_diagnostic_data_dict["system_information"]["hostname"]}_diag_data.json'
        # No need to parse out - backup entire response
        ihealth_diagnostic_data_json_string = json.dumps(ihealth_diagnostic_data_dict, indent=4)
        with open(filename_string, 'w') as output_file:
            output_file.write(ihealth_diagnostic_data_json_string)
