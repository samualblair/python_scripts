# Created by: Michael Johnson - 09-29-2025
# Paring code to deliver f5_xc_dns_lb configurations

# import required modules
import os
import json
import time
# Use Python requests Library to send API calls
import requests

def f5_xc_deliver_configs(f5_xc_json:str, f5xc_object_type:str) -> None:
    """
    Takes JSON Configuraiton file and delivers to F5 DC (XC) SaaS Platform via REST API
    """

    if f5xc_object_type == "test":

        # TESTING - Perform Test GET to make sure permissions and cert are correct
        print("Testing Connection to F5 XC DNS - Checking DNS Zones - GET")
        f5_xc_get_dns_zones()
        print("... resting 5 sec")
        time.sleep(2)

    else:
        with open(f5_xc_json, 'r') as input_file:
            f5_xc_json_config_string = input_file.read()


            payload_dictionary = json.loads(f5_xc_json_config_string)

            list_of_name_types = ["1_healthcheck", "2_pool", "3_dnslb"]

            if f5xc_object_type in list_of_name_types:
                try:
                    #print(payload_dictionary["metadata"]["name"])
                    f5xc_object_name = payload_dictionary["metadata"]["name"]
                except KeyError:
                    print("Unable to find object name in json payload - Quitting")
                    return

            if f5xc_object_type == "4_records":
                try:
                    #print(payload_dictionary["rrset"]["lb_record"]["name"])
                    f5xc_dns_zone_name = payload_dictionary["dns_zone_name"]
                    f5xc_dns_zone_rr_group = payload_dictionary["group_name"]
                    f5xc_dns_zone_rr_record_name = payload_dictionary["rrset"]["lb_record"]["name"]
                    # f5xc_dns_zone_rr_type = "lb_record"
                    f5xc_dns_zone_rr_get_type = "DNSLB"
                except KeyError:
                    print("Unable to find dns name in json payload - Quitting")
                    return

            if f5xc_object_type == "1_healthcheck":
                # Step 1 - Create healthchecks
                print(f" F5 XC DNS - Creating Health Monitor - POST for: {f5xc_object_name}")
                f5_xc_create_dns_lb_healthcheck(f5_xc_json_config_string)
                time.sleep(2)
                print(f" F5 XC DNS - Checking Health Monitor - GET for: {f5xc_object_name}")
                f5_xc_get_dns_lb_healthcheck(f5xc_object_name)
                time.sleep(2)

            elif f5xc_object_type == "2_pool":
                # Step 2 - Create Pools
                print(f" F5 XC DNS - Creating DNS Pool - POST for: {f5xc_object_name}")
                f5_xc_create_dns_lb_pool(f5_xc_json_config_string)
                time.sleep(2)
                print(f" F5 XC DNS - Checking DNS Pool - GET for: {f5xc_object_name}")
                f5_xc_get_dns_lb_pool(f5xc_object_name)
                time.sleep(2)

            elif f5xc_object_type == "3_dnslb":
                # Step 3 - Create DNS LB Instances
                print(f" F5 XC DNS - Creating DNS LB - POST for: {f5xc_object_name}")
                f5_xc_create_dns_lb_dnslb(f5_xc_json_config_string)
                time.sleep(2)
                print(f" F5 XC DNS - Checking DNS LB - GET for: {f5xc_object_name}")
                f5_xc_get_dns_lb_dnslb(f5xc_object_name)
                time.sleep(2)

            elif f5xc_object_type == "4_records":
                # Step 4 - Create DNS Records
                print(f" F5 XC DNS - Creating DNS Record - POST for: {f5xc_dns_zone_rr_record_name}")
                f5_xc_create_dns_lb_rrecord(f5_xc_json_config_string, f5xc_dns_zone_name, f5xc_dns_zone_rr_group)
                time.sleep(2)
                print(f" F5 XC DNS - Checking DNS Record - GET for: {f5xc_dns_zone_rr_record_name}")
                f5_xc_get_dns_lb_rrecord(f5xc_dns_zone_name, f5xc_dns_zone_rr_group, f5xc_dns_zone_rr_record_name, f5xc_dns_zone_rr_get_type)
                time.sleep(2)

            else:
                print("No type matched - exiting")



def f5_xc_create_dns_lb_healthcheck(f5_xc_json:str) -> None:
    """
    Creates XC DNS-LB Healthcheck
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """
    
    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_lb_health_checks"
    payload = f5_xc_json

    headers = {
    'Content-Type': 'application/json'
    }

    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))

    if response.status_code == 429:
        print(f"Hitting Rate Limits due to response code was: {response.status_code}")
        print("Waiting 10 sec...")
        time.sleep(10)
        print("Continuing...and Trying Again")
        response = requests.request(
            "POST", url, headers=headers, data=payload, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))

    print(f"The response code was: {response.status_code}")
    # print(response.text)

def f5_xc_get_dns_lb_healthcheck(f5xc_object_name:str) -> None:
    """
    Checks XC DNS-LB Healthcheck
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """
    
    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_lb_health_checks/{f5xc_object_name}"
    response = requests.request("GET", url, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))
    
    if response.status_code == 409:
        print(f"The Object Probably Already Existed - The response code was: {response.status_code}")
    else:    
        print(f"The response code was: {response.status_code}")
    # print(response.text)

    # To load response as object
    # json_dict = response.json
    # Then to print back as formated string
    # json_string = json.dumps(json_dict, indent=4)

def f5_xc_create_dns_lb_pool(f5_xc_json:str) -> None:
    """
    Creates XC DNS-LB Pool
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """
    
    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_lb_pools"
    payload = f5_xc_json

    headers = {
    'Content-Type': 'application/json'
    }
    
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))

    if response.status_code == 429:
        print(f"Hitting Rate Limits due to response code was: {response.status_code}")
        print("Waiting 10 sec...")
        time.sleep(10)
        print("Continuing...and Trying Again")
        response = requests.request(
            "POST", url, headers=headers, data=payload, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))


    print(f"The response code was: {response.status_code}")
    # print(response.text)

def f5_xc_get_dns_lb_pool(f5xc_object_name:str) -> None:
    """
    Checks XC DNS-LB Pool
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """
    
    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_lb_pools/{f5xc_object_name}"
    response = requests.request("GET", url, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))
    
    if response.status_code == 409:
        print(f"The Object Probably Already Existed - The response code was: {response.status_code}")
    else:    
        print(f"The response code was: {response.status_code}")
    # print(response.text)

    # To load response as object
    # json_dict = response.json
    # Then to print back as formated string
    # json_string = json.dumps(json_dict, indent=4)


def f5_xc_create_dns_lb_dnslb(f5_xc_json:str) -> None:
    """
    Creates XC DNS-LB Pool
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """

    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_load_balancers"
    payload = f5_xc_json

    headers = {
    'Content-Type': 'application/json'
    }
    
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))

    if response.status_code == 429:
        print(f"Hitting Rate Limits due to response code was: {response.status_code}")
        print("Waiting 10 sec...")
        time.sleep(10)
        print("Continuing...and Trying Again")
        response = requests.request(
            "POST", url, headers=headers, data=payload, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))

    print(f"The response code was: {response.status_code}")
    # print(response.text)

def f5_xc_get_dns_lb_dnslb(f5xc_object_name:str) -> None:
    """
    Checks XC DNS-LB Pool
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """
    
    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_load_balancers/{f5xc_object_name}"
    response = requests.request("GET", url, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))
    
    if response.status_code == 409:
        print(f"The Object Probably Already Existed - The response code was: {response.status_code}")
    else:    
        print(f"The response code was: {response.status_code}")
    # print(response.text)

    # To load response as object
    # json_dict = response.json
    # Then to print back as formated string
    # json_string = json.dumps(json_dict, indent=4)


def f5_xc_create_dns_lb_rrecord(f5_xc_json:str, f5xc_dns_zone_name:str, f5xc_dns_zone_rr_group:str) -> None:
    """
    Creates XC DNS-LB Pool
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """
    
    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_zones/{f5xc_dns_zone_name}/rrsets/{f5xc_dns_zone_rr_group}"
    payload = f5_xc_json

    headers = {
    'Content-Type': 'application/json'
    }
    
    response = requests.request(
        "POST", url, headers=headers, data=payload, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))
    
    if response.status_code == 429:
        print(f"Hitting Rate Limits due to response code was: {response.status_code}")
        print("Waiting 10 sec...")
        time.sleep(10)
        print("Continuing...and Trying Again")
        response = requests.request(
            "POST", url, headers=headers, data=payload, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))

    print(f"The response code was: {response.status_code}")
    # print(response.text)

def f5_xc_get_dns_lb_rrecord(f5xc_dns_zone_name:str, f5xc_dns_zone_rr_group:str, f5xc_dns_zone_rr_record_name:str, f5xc_dns_zone_rr_get_type:str) -> None:
    """
    Checks XC DNS-LB Pool
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """

    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_zones/{f5xc_dns_zone_name}/rrsets/{f5xc_dns_zone_rr_group}/{f5xc_dns_zone_rr_record_name}/{f5xc_dns_zone_rr_get_type}"
    response = requests.request("GET", url, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))
    
    if response.status_code == 409:
        print(f"The Object Probably Already Existed - The response code was: {response.status_code}")
    else:    
        print(f"The response code was: {response.status_code}")
    # print(response.text)

    # To load response as object
    # json_dict = response.json
    # Then to print back as formated string
    # json_string = json.dumps(json_dict, indent=4)

def f5_xc_get_dns_zones() -> None:
    """
    Creates XC DNS-LB Healthcheck
    Takes configuration json
    Expects 'f5xc_tennant_short_id' and 'f5xc_namespace' strings to be defined
    """
    
    url = f"https://{f5xc_tennant_short_id}.console.ves.volterra.io/api/config/dns/namespaces/{f5xc_namespace}/dns_zones"
    response = requests.request("GET", url, verify=server_cert_ca_location, cert=(client_cert_location, client_key_location))
    print(f"When Checking Zones - the response code was: {response.status_code}")
    # print(response.text)


if __name__ == "__main__":
    # Assign directory to parse and Deliver
    
    # Object Type can be: test , 1_healthcheck , 2_pool , 3_dnslb , 4_records
    # f5xc_object_type_chosen = "test"
    # f5xc_object_type_chosen = "4_records"
    f5xc_object_type_chosen = input('Please Enter Type (all or test , 1_healthcheck , 2_pool , 3_dnslb , 4_records ) \n')

    print('Expecting a folder with these files (unencrypted) - private_key_file.pem , public_cert_file.pem, console-ves-volterra-io-chain.pem\n')
    base_cert_directory = input('Please enter folder with certificates, and no trailing "/" (HINT: may navigate back a folder with ../FOLDERNAME )\n')
    client_key_location = f'{base_cert_directory}/private_key_file.pem'
    client_cert_location = f'{base_cert_directory}/public_cert_file.pem'
    server_cert_ca_location = f'{base_cert_directory}/console-ves-volterra-io-chain.pem'
    # client_key_location = '/folder/path/certs/private_key_file.pem'
    # client_cert_location = '/folder/path/certs/public_cert_file.pem'
    # server_cert_ca_location ='/folder/path/certs/console-ves-volterra-io-chain.pem'
    #client_key_pass = input('Client Key Decryption Password\n')
    
    directory = input('Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )\n')
    # directory = './jinja_test'
    # directory = "./jinja_rendered"
    # directory = "retry"

    f5xc_tennant_short_id = input('Please enter Short Tennant ID such as: exampletennant\n')
    f5xc_tennant_long_id = input('Please enter Long Tennant ID such as: exampletennant-longid \n')
    f5xc_namespace = input('Please enter namespace - For DNS-LB it should be: system \n')
    # f5xc_tennant_short_id = "exampletennant"
    # f5xc_tennant_long_id = "exampletennant-longid"
    # f5xc_namespace = "system"
    # client_key_location = input('Please enter an Full path to Client cert private key \n')
    # client_cert_location = input('Please enter an Full path to Client cert public key \n')
    # server_cert_ca_location = input('Please enter an Full path to Server CA or trust chain \n')

    # TODO: Add support for encrypted client key
    # client_key_pass = input('Client Key Decryption Password\n')

    # Walk directory tree and record for later use
    recursive_folder_list = []
    recursive_lists_dict = {}
    # recursive_lists_dict["recursive_folder_list_0_test"] = ["test"]
    recursive_lists_dict["recursive_folder_list_1_healthcheck"] = []
    recursive_lists_dict["recursive_folder_list_2_pool"] = []
    recursive_lists_dict["recursive_folder_list_3_dnslb"] = []
    recursive_lists_dict["recursive_folder_list_4_records"] = []


    if (f5xc_object_type_chosen == "test"):
        pass

    else:
        for currentpath, folders, files in os.walk(directory):
            for folder in folders:
                # print(os.path.join(currentpath, file))
                recursive_folder_list.append(os.path.join(currentpath, folder))

        # Sort Folders into specific lists
        for folder in recursive_folder_list:
            if folder.find("1_healthcheck") > 0:
                recursive_lists_dict["recursive_folder_list_1_healthcheck"].append(folder)
            elif folder.find("2_pool") > 0:
                recursive_lists_dict["recursive_folder_list_2_pool"].append(folder)
            elif folder.find("3_dnslb") > 0:
                recursive_lists_dict["recursive_folder_list_3_dnslb"].append(folder)
            elif folder.find("4_records") > 0:
                recursive_lists_dict["recursive_folder_list_4_records"].append(folder)
            else:
                print(f"Skipping Unexpected Folder: {folder}")

        # print(recursive_lists_dict["recursive_folder_list_1_healthcheck"])
        # print(recursive_lists_dict["recursive_folder_list_2_pool"])
        # print(recursive_lists_dict["recursive_folder_list_3_dnslb"])
        # print(recursive_lists_dict["recursive_folder_list_4_records"])

    # print(sys.argv[1]) --- Only navigates into folder - does not check base folder currently
    try:

        # # All folders Recursivly but in no order

        # for folder_name in recursive_folder_list:
        #     for file_name in os.listdir(folder_name):
        #         file_contents = os.path.join(folder_name, file_name)
        #         # checking if it is a file
        #         if os.path.isfile(file_contents):
        #             try:
        #                 # Only try to parse file if it is name ends with .json
        #                 if file_name[-5:] == ".json":
        #                     f5_xc_deliver_configs(file_contents, f5xc_object_type_chosen)
        #             # Catch when file is not parsable UTF 8 or similar
        #             except UnicodeDecodeError:
        #                 print('Fail to read file - ' + file_name + ' : Is this a file to be read?')


        # # All expected folders - in order

        # Test Connection to F5 XC
        if (f5xc_object_type_chosen == "test"):
            f5_xc_deliver_configs("test", "test")

        # Configure 1_healthcheck
        if (f5xc_object_type_chosen == "all") or (f5xc_object_type_chosen == "1_healthcheck"):
            for folder_name in recursive_lists_dict["recursive_folder_list_1_healthcheck"]:
                for file_name in os.listdir(folder_name):
                    file_contents = os.path.join(folder_name, file_name)
                    # checking if it is a file
                    if os.path.isfile(file_contents):
                        try:
                            # Only try to parse file if it is name ends with .json
                            if file_name[-5:] == ".json":
                                f5_xc_deliver_configs(file_contents, "1_healthcheck")
                                # print(f"Found {file_name} as type 1_healthcheck")
                        # Catch when file is not parsable UTF 8 or similar
                        except UnicodeDecodeError:
                            print('Fail to read file - ' + file_name + ' : Is this a file to be read?')

        # Configure 2_pool
        if (f5xc_object_type_chosen == "all") or (f5xc_object_type_chosen == "2_pool"):
            for folder_name in recursive_lists_dict["recursive_folder_list_2_pool"]:
                for file_name in os.listdir(folder_name):
                    file_contents = os.path.join(folder_name, file_name)
                    # checking if it is a file
                    if os.path.isfile(file_contents):
                        try:
                            # Only try to parse file if it is name ends with .json
                            if file_name[-5:] == ".json":
                                f5_xc_deliver_configs(file_contents, "2_pool")
                                # print(f"Found {file_name} as type 2_pool")
                        # Catch when file is not parsable UTF 8 or similar
                        except UnicodeDecodeError:
                            print('Fail to read file - ' + file_name + ' : Is this a file to be read?')

        # Configure 3_dnslb
        if (f5xc_object_type_chosen == "all") or (f5xc_object_type_chosen == "3_dnslb"):
            for folder_name in recursive_lists_dict["recursive_folder_list_3_dnslb"]:
                for file_name in os.listdir(folder_name):
                    file_contents = os.path.join(folder_name, file_name)
                    # checking if it is a file
                    if os.path.isfile(file_contents):
                        try:
                            # Only try to parse file if it is name ends with .json
                            if file_name[-5:] == ".json":
                                f5_xc_deliver_configs(file_contents, "3_dnslb")
                                # print(f"Found {file_name} as type 3_dnslb")
                        # Catch when file is not parsable UTF 8 or similar
                        except UnicodeDecodeError:
                            print('Fail to read file - ' + file_name + ' : Is this a file to be read?')

        # Configure 4_records
        if (f5xc_object_type_chosen == "all") or (f5xc_object_type_chosen == "4_records"):
            for folder_name in recursive_lists_dict["recursive_folder_list_4_records"]:
                for file_name in os.listdir(folder_name):
                    file_contents = os.path.join(folder_name, file_name)
                    # checking if it is a file
                    if os.path.isfile(file_contents):
                        try:
                            # Only try to parse file if it is name ends with .json
                            if file_name[-5:] == ".json":
                                f5_xc_deliver_configs(file_contents, "4_records")
                                # print(f"Found {file_name} as type 4_records")
                        # Catch when file is not parsable UTF 8 or similar
                        except UnicodeDecodeError:
                            print('Fail to read file - ' + file_name + ' : Is this a file to be read?')

    except IndexError:
        print('Issue with file - ' + file_name)

    # # Alternativly deliver single file
    # # print(sys.argv[1])
    # try:
    #     f5_xc_deliver_configs(sys.argv[1])
    # # Catch when file is not parsable UTF 8 or similar
    # except UnicodeDecodeError:
    #     print('Fail to read file - ' + sys.argv[1] + ' : Is this a file to be read?')
    # except IndexError:
    #     f5_xc_deliver_configs()
