# Created by: Michael Johnson - 09-29-2025
# Paring code to parse iniital json verion of bigip.conf dictionary for building ltm reports

# import required modules
import json
import sys


def ltm_conversion_file(bigip_conf_filename:str="bigip_ltm_dict.json") -> None:
    """
    Reviews JSON files previously created from lib_f5_tmsh_standard_direct_parse json converter, outputs custom data
    WARNING: Only works with supported features (don't expect every config line to be present).
    """

    with open(bigip_conf_filename, 'r') as vars_file:
        source = json.load(vars_file)


    # Wanted virtual server name and IP of vs

    new_config_dict = {}

    # Convert Wide IP

    # Convert LTM Virtual Server
    for item in source:
        try:
            if item["ltm"] == "virtual":
                for subitem in item:
                    try:
                        if subitem[0:8] == "/Common/":
                            new_config_dict[subitem[8:]] = {}
                            new_config_dict[subitem[8:]]["lb-vs"] = item[subitem]
                            # new_config_dict[subitem[8:]] = item[subitem]
                    except IndexError:
                        continue
        except KeyError:
            continue

    # Convert LTM Pool
    for item in source:
        try:
            if item["ltm"] == "pool":
                for subitem in item:
                    try:
                        if subitem[0:8] == "/Common/":
                            new_config_dict[subitem[8:]] = {}
                            new_config_dict[subitem[8:]]["lb-pool"] = item[subitem]
                            # new_config_dict[subitem[8:]] = item[subitem]
                    except IndexError:
                        continue
        except KeyError:
            continue

    # Convert Pool Members / Nodes
    for item in source:
        try:
            if item["ltm"] == "node":
                for subitem in item:
                    try:
                        if subitem[0:8] == "/Common/":
                            new_config_dict[subitem[8:]] = {}
                            new_config_dict[subitem[8:]]["lb-node"] = item[subitem]
                            # new_config_dict[subitem[8:]] = item[subitem]
                    except IndexError:
                        continue
        except KeyError:
            continue

    # Convert Pool Members / Nodes
    for item in source:
        try:
            if item["ltm"] == "virtual-address":
                for subitem in item:
                    try:
                        if subitem[0:8] == "/Common/":
                            new_config_dict[subitem[8:]] = {}
                            new_config_dict[subitem[8:]]["lb-va"] = item[subitem]
                            # new_config_dict[subitem[8:]] = item[subitem]
                    except IndexError:
                        continue
        except KeyError:
            continue

    # # Convert Healthchecks aka monitor
    # for item in source:
    #     try:
    #         if item["gtm"] == "monitor":
    #             for subitem in item:
    #                 try:
    #                     key_not_found = True
    #                     if subitem[0:8] == "/Common/":
    #                         new_config_dict[subitem[8:]] = {}
    #                         # new_config_dict[subitem[8:]] = item[subitem]
    #                         try:
    #                             if item["http"]:
    #                                 new_config_dict[subitem[8:]]["monitor http"] = item[subitem]
    #                                 key_not_found = False
    #                         except KeyError:
    #                             pass
    #                         try:
    #                             if item["https"]:
    #                                 new_config_dict[subitem[8:]]["monitor https"] = item[subitem]
    #                                 key_not_found = False
    #                         except KeyError:
    #                             pass
    #                         try:
    #                             if item["sip"]:
    #                                 new_config_dict[subitem[8:]]["monitor sip"] = item[subitem]
    #                                 key_not_found = False
    #                         except KeyError:
    #                             pass
    #                         try:
    #                             if item["smtp"]:
    #                                 new_config_dict[subitem[8:]]["monitor smtp"] = item[subitem]
    #                                 key_not_found = False
    #                         except KeyError:
    #                             pass
    #                         # Show error if key is not found - must be unexpected Monitor type
    #                         if key_not_found:
    #                             print("Not an an expected Monitor - type is '\\n")
    #                             print(item)
    #                             print("\\n'")
    #                 except IndexError:
    #                     continue
    #     except KeyError:
    #         continue


    # Convert to nice indent format
    json_string = json.dumps(new_config_dict, indent=4)
    # print(json_string)

    with open(bigip_conf_filename[:-5] + '_converted.json', 'w') as input_file:
        input_file.write(json_string + "\n")



if __name__ == "__main__":
    # print(sys.argv[1])
    try:
        ltm_conversion_file(sys.argv[1])
    # Catch when file is not parsable UTF 8 or similar
    except UnicodeDecodeError:
        print('Fail to read file - ' + sys.argv[1] + ' : Is this a file to be read?')
    except IndexError:
        ltm_conversion_file()



