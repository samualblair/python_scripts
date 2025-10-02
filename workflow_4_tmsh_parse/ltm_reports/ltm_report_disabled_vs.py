# Created by: Michael Johnson - 09-29-2025
# Paring code to create reports from converted json of a bigip.conf file such as 'common_bigip_dict_converted.json'

# import required modules
import json
import sys
import csv
# from jinja2 import Environment, FileSystemLoader


def build_ltm_report_vars(bigip_ltm_dict:dict) -> None:
    """
    Uses referenced passed to it to create vars for ltm report
    """

    # Wanted virtual server name and IP of vs
    # ltm_report_vars_dict = {}
    list_of_disabled_vs_names = []

    # Search for Disabled Virtual Servers
    for object in bigip_ltm_dict:
        try:
            if bigip_ltm_dict[object]["lb-vs"]["disabled"]:
                list_of_disabled_vs_names.append(object)
        except KeyError:
            pass
    
    # print(list_of_disabled_vs_names)

    # build_ltm_vs_removal(list_of_disabled_vs_names)
    build_ltm_vs_removal_list(list_of_disabled_vs_names,"_Disabled_ALL")

    # Compare against previous List
    compare_lists(list_of_disabled_vs_names)


    # Compile list of Profiles, that are used by disabled virtual servers
    unused_profiles = {}

    for disabled_vs in list_of_disabled_vs_names:
        try:
            for profile_name in bigip_ltm_dict[disabled_vs]["lb-vs"]["profiles"]:
                unused_profiles[profile_name] = profile_name
        except KeyError:
            print(f"No Profiles found in {disabled_vs}")

    # print(unused_profiles)

    for object in bigip_ltm_dict:
        try:
            if bigip_ltm_dict[object]["lb-vs"]:
                try:
                    if bigip_ltm_dict[object]["lb-vs"]["disabled"]:
                        pass
                except KeyError:
                    for profile in bigip_ltm_dict[object]["lb-vs"]["profiles"]:
                        try:
                            # Profile still in use by non-disabled Virtual Server
                            unused_profiles.pop(profile)
                            # print(f"This profile is still in use - {profile} by {object}")
                        except KeyError:
                            # print("Pop Failed")
                            pass
        except KeyError:
            # print(f"not a vs {object}")
            pass


    # print(unused_profiles)
    build_ltm_vs_removal_list(unused_profiles,"_unused_profiles")

def compare_lists(csv_ready_list:list) -> None:
    """
    Function to compare removal lists
    """

    import_csv_dict = { }

    try:
        # TODO: Make list name dynamic - currently expects a list file with virtual server names
        with open('requested_cleanup_vs.csv', 'r') as csv_vars_file:
            csv_file = csv.DictReader(csv_vars_file)
            csv_headers = []
            for headers in csv_file.fieldnames:
                csv_headers.append(headers)
            for row in csv_file:
                # Create an old/new dictionary
                import_csv_dict[row['Virtual Server Name']] = {}
                for header_in_list in csv_headers:
                    import_csv_dict[row['Virtual Server Name']][header_in_list] = row[header_in_list]

        # print(import_csv_dict)    
    except FileNotFoundError:
        print("Unable to find Monitor Name Swap List - old file found")

    names_to_remove = []
    flagged_for_removal_not_disabled = []
    orignal_removal_list = []

    # for item in csv_ready_list:
    #    names_to_remove.append(item)
    for item in csv_ready_list:
       orignal_removal_list.append(item)

    # print(names_to_remove)
    # print(flagged_for_removal_not_disabled)
    # print(orignal_removal_list)

    for item in import_csv_dict:
        try:
            current_item = import_csv_dict[item]
            current_dict_item = import_csv_dict[item]["Virtual Server Name"]
            if current_dict_item in csv_ready_list:
                names_to_remove.append(current_dict_item)
                orignal_removal_list.remove(current_dict_item)
            else:
                flagged_for_removal_not_disabled.append(current_dict_item)
        except KeyError:
            print(f"waringing Key Error {current_item}")

    #print(names_to_remove)
    # print(f"Flagged for removal but not on DISABLED list - {flagged_for_removal_not_disabled}")
    # print(f"Not-Flagged for removal Yet but on DISABLED list - {orignal_removal_list}")

    build_ltm_vs_removal(flagged_for_removal_not_disabled,"_Manual_Removal_Request_Flagged")
    build_ltm_vs_removal(orignal_removal_list,"_Other_Disabled")
    build_ltm_vs_removal(names_to_remove,"_Confirmed_to_Remove")

def build_ltm_vs_removal_list(csv_ready_dictionary:list,file_name_add:str="") -> None:
    """
    Function to take a dictionary ready to go ltm_report and save out as a csv file
    Writes to ltm_report.csv
    """

    # TODO: Make CSV File

    ltm_csv_dict = {}

    for entry in csv_ready_dictionary:
        ltm_csv_dict[entry] = {}
        ltm_csv_dict[entry]["# Virtual Servers Disabled"] = entry

    csv_fieldnames = \
        ["# Virtual Servers Disabled"]

    # Write out to csv File by keying in on dictionary header names
    with open('ltm_removal_report_list' + file_name_add + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
        writer.writeheader()
        for item in ltm_csv_dict:
            writer.writerow(ltm_csv_dict[item])


def build_ltm_vs_removal(csv_ready_dictionary:list,file_name_add:str="") -> None:
    """
    Function to take a dictionary ready to go ltm_report and save out as a csv file
    Writes to ltm_report.csv
    """

    # TODO: Make CSV File

    ltm_csv_dict = {}

    for entry in csv_ready_dictionary:
        ltm_csv_dict[entry] = {}
        ltm_csv_dict[entry]["# Virtual Servers to Remove"] = "tmsh delete ltm virtual " + entry

    csv_fieldnames = \
        ["# Virtual Servers to Remove"]

    # Write out to csv File by keying in on dictionary header names
    with open('ltm_removal_report' + file_name_add + '.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
        writer.writeheader()
        for item in ltm_csv_dict:
            writer.writerow(ltm_csv_dict[item])


def build_ltm_report_json(json_ready_dictionary:dict) -> None:
    """
    Function to take a dictionary ready to go ltm_report and save out as a json file
    Writes to ltm_report.json
    """

    pass

    # TODO: Make JSON File

    # # Convert to nice indent format
    # json_string = json.dumps(new_config_dict, indent=4)
    # # print(json_string)

    # with open(bigip_conf_filename[:-5] + '_report.json', 'w') as input_file:
    #     input_file.write(json_string + "\n")

def build_ltm_report_csv(csv_ready_dictionary:dict) -> None:
    """
    Function to take a dictionary ready to go ltm_report and save out as a csv file
    Writes to ltm_report.csv
    """

    pass

    # TODO: Make CSV File

    # ltm_csv_dict = {}

    # for entry in csv_ready_dictionary:
    #     ltm_csv_dict[entry] = {}
    #     # ltm_csv_dict[entry]["global_dns_name"] = csv_ready_dictionary[entry]["global_dns_name"]
    #     ltm_csv_dict[entry]["gtm_dns_name"] = csv_ready_dictionary[entry]["gtm_dns_name"]
    #     ltm_csv_dict[entry]["xc_dns_name"] = csv_ready_dictionary[entry]["xc_dns_name"]
    #     ltm_csv_dict[entry]["dns_short_name"] = csv_ready_dictionary[entry]["dns_short_name"]
    #     ltm_csv_dict[entry]["gtm_dns_domain_name"] = csv_ready_dictionary[entry]["gtm_dns_domain_name"]
    #     ltm_csv_dict[entry]["xc_dns_domain_name"] = csv_ready_dictionary[entry]["xc_dns_domain_name"]
    #     ltm_csv_dict[entry]["xc_dns_zone_name"] = csv_ready_dictionary[entry]["xc_dns_zone_name"]
    #     ltm_csv_dict[entry]["xc_rrset_name"] = csv_ready_dictionary[entry]["xc_rrset_name"]
    #     ltm_csv_dict[entry]["xc_dns_lb_name"] = csv_ready_dictionary[entry]["xc_dns_lb_name"]
    #     ltm_csv_dict[entry]["dns_type"] = csv_ready_dictionary[entry]["dns_type"]
    #     ltm_csv_dict[entry]["xc_dns_pool_name"] = csv_ready_dictionary[entry]["xc_dns_pool_name"]
    #     try:
    #         ltm_csv_dict[entry]["xc_dns_lb_method"] = csv_ready_dictionary[entry]["xc_dns_lb_method"]
    #     except KeyError:
    #         print(f"{{ERROR - Unable to find xc_dns_lb_method for {csv_ready_dictionary[entry]["gtm_dns_name"]} }}")
    #         ltm_csv_dict[entry]["xc_dns_lb_method"] = "PRIORITY"
    #     ltm_csv_dict[entry]["dc_primary"] = csv_ready_dictionary[entry]["dc_primary"]
    #     ltm_csv_dict[entry]["dc_primary_gtm_member_1_ip"] = csv_ready_dictionary[entry]["dc_primary_gtm_member_1_ip"]
    #     ltm_csv_dict[entry]["dc_secondary"] = csv_ready_dictionary[entry]["dc_secondary"]
    #     ltm_csv_dict[entry]["dc_secondary_gtm_member_2_ip"] = csv_ready_dictionary[entry]["dc_secondary_gtm_member_2_ip"]
    #     ltm_csv_dict[entry]["xc_pool_monitor__monitor_name"] = csv_ready_dictionary[entry]["xc_pool_monitor"]["monitor_name"]
    #     try:
    #         ltm_csv_dict[entry]["xc_pool_monitor__send"] = csv_ready_dictionary[entry]["xc_pool_monitor"]["send"]
    #     except KeyError:
    #         ltm_csv_dict[entry]["xc_pool_monitor__send"] = ""
    #     try:
    #         ltm_csv_dict[entry]["xc_pool_monitor__recv"] = csv_ready_dictionary[entry]["xc_pool_monitor"]["recv"]
    #     except KeyError:
    #         ltm_csv_dict[entry]["xc_pool_monitor__recv"] = ""
    #     try:
    #         ltm_csv_dict[entry]["xc_pool_monitor__description"] = csv_ready_dictionary[entry]["xc_pool_monitor"]["description"]
    #     except KeyError:
    #         ltm_csv_dict[entry]["xc_pool_monitor__description"] = ""
    #     try:
    #         ltm_csv_dict[entry]["xc_pool_monitor__monitor_type"] = csv_ready_dictionary[entry]["xc_pool_monitor"]["monitor type"]
    #     except KeyError:
    #         ltm_csv_dict[entry]["xc_pool_monitor__monitor_type"] = ""

    # csv_fieldnames = \
    #     ["report_var_1",
    #      "report_var2", "report_var3",
    #      "report_var4"]

    # # Write out to csv File by keying in on dictionary header names
    # with open('ltm_report' + '.csv', 'w', newline='') as csvfile:
    #     writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
    #     writer.writeheader()
    #     for item in ltm_csv_dict:
    #         writer.writerow(ltm_csv_dict[item])

if __name__ == "__main__":
    # print(sys.argv[1])

    # Expect script to be run pointing to a converted json such as 'common_bigip_dict_converted.json'
    try:

        with open(sys.argv[1], 'r') as vars_file:
            source_ltm_json = json.load(vars_file)

            build_ltm_report_vars(source_ltm_json)
        
    # Catch when file is not parsable UTF 8 or similar
    except UnicodeDecodeError:
        print('Fail to read file - ' + sys.argv[1] + ' : Is this a file to be read?')
    except IndexError:
        build_ltm_report_vars()

