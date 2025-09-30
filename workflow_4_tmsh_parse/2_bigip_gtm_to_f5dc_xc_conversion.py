# Created by: Michael Johnson - 09-29-2025
# Paring code to parse iniital json verion of bigip_gtm.conf to f5dc (xc) ready dictionary

# import required modules
import json
import sys
import csv
from jinja2 import Environment, FileSystemLoader

def gtm_conversion_file(bigip_conf_filename:str="bigip_gtm_dict.json") -> None:
    """
    Reviews JSON files previously created from lib_f5_tmsh_standard_direct_parse (gtm version) json converter, outputs custom data
    WARNING: Only works with supported features (don't expect every config line to be present).
    """

    with open(bigip_conf_filename, 'r') as vars_file:
        source = json.load(vars_file)


    # Wanted virtual server name and IP of vs

    new_config_dict = {}

    # Convert Wide IP
    for item in source:
        try:
            if item["gtm"] == "wideip":
                for subitem in item:
                    try:
                        key_not_found = True
                        if subitem[0:8] == "/Common/":
                            new_config_dict[subitem[8:]] = {}
                            # new_config_dict[subitem[8:]] = item[subitem]
                            try:
                                if item["a"]:
                                    new_config_dict[subitem[8:]]["wideip a"] = item[subitem]
                                    key_not_found = False
                            except KeyError:
                                pass
                            # Show error if key is not found - must be unexpected Monitor type
                            if key_not_found:
                                print("Not an an expected Wide-IP Type - type is '\\n")
                                print(item)
                                print("\\n'")
                    except IndexError:
                        continue
        except KeyError:
            continue

    # Convert Pool
    for item in source:
        try:
            if item["gtm"] == "pool":
                for subitem in item:
                    try:
                        if subitem[0:8] == "/Common/":
                            new_config_dict[subitem[8:]] = {}
                            new_config_dict[subitem[8:]]["pool"] = item[subitem]
                            # new_config_dict[subitem[8:]] = item[subitem]
                    except IndexError:
                        continue
        except KeyError:
            continue

    # Convert Server aka Pool Members / Nodes
    for item in source:
        try:
            if item["gtm"] == "server":
                for subitem in item:
                    try:
                        if subitem[0:8] == "/Common/":
                            new_config_dict[subitem[8:]] = {}
                            new_config_dict[subitem[8:]]["server"] = item[subitem]
                            # new_config_dict[subitem[8:]] = item[subitem]
                    except IndexError:
                        continue
        except KeyError:
            continue

    # Convert Healthchecks aka monitor
    for item in source:
        try:
            if item["gtm"] == "monitor":
                for subitem in item:
                    try:
                        key_not_found = True
                        if subitem[0:8] == "/Common/":
                            new_config_dict[subitem[8:]] = {}
                            # new_config_dict[subitem[8:]] = item[subitem]
                            try:
                                if item["http"]:
                                    new_config_dict[subitem[8:]]["monitor http"] = item[subitem]
                                    key_not_found = False
                            except KeyError:
                                pass
                            try:
                                if item["https"]:
                                    new_config_dict[subitem[8:]]["monitor https"] = item[subitem]
                                    key_not_found = False
                            except KeyError:
                                pass
                            try:
                                if item["sip"]:
                                    new_config_dict[subitem[8:]]["monitor sip"] = item[subitem]
                                    key_not_found = False
                            except KeyError:
                                pass
                            try:
                                if item["smtp"]:
                                    new_config_dict[subitem[8:]]["monitor smtp"] = item[subitem]
                                    key_not_found = False
                            except KeyError:
                                pass
                            # Show error if key is not found - must be unexpected Monitor type
                            if key_not_found:
                                print("Not an an expected Monitor - type is '\\n")
                                print(item)
                                print("\\n'")
                    except IndexError:
                        continue
        except KeyError:
            continue


    # Convert to nice indent format
    json_string = json.dumps(new_config_dict, indent=4)
    # print(json_string)

    with open(bigip_conf_filename[:-5] + '_converted.json', 'w') as input_file:
        input_file.write(json_string + "\n")

    build_f5dc_xc_config_vars(new_config_dict)

def build_f5dc_xc_config_vars(bigip_gtm_dict:dict) -> None:
    """
    Uses dictionarty passed to it to create f5dc_xc config vars
    """

    xc_vars_dict = {}

    list_of_dns_lb_names = []

    list_of_dns_pools_gtm_no_fallback = []
    list_of_dns_pools_gtm_not_ga_priority_lb_mode = []
    list_of_dns_pools_gtm_with_unexpected_members = []


    # Parse Items to obtain list of dns names
    for item in bigip_gtm_dict:
        try:
            if bigip_gtm_dict[item]["wideip a"]:
                list_of_dns_lb_names.append(item)
        except KeyError:
            pass
    
    # Prepare dictionary entries
    for dns_name in list_of_dns_lb_names:

        # Base, Wide-IP/DNS-LB Info
        xc_vars_dict[dns_name] = {}
        xc_vars_dict[dns_name]["global_dns_name"] = dns_name
        xc_vars_dict[dns_name]["gtm_dns_name"] = dns_name
        xc_vars_dict[dns_name]["xc_dns_name"] = dns_name
        xc_vars_dict[dns_name]["xc_rrset_name"] = ""

        # TODO: ENSURE DNS ZONE NAME IS SPECIFIED FOR XC - xc_dns_zone_name , 
        xc_vars_dict[dns_name]["xc_dns_zone_name"] = "xczone.example.com"

        # XC TENNANT ID MANUALLY 
        # TODO: Take in Tennat ID from file or user input
        xc_vars_dict[dns_name]["xc_long_tennat_id"] = "exampletennant-longid"
        xc_vars_dict[dns_name]["xc_short_tennat_id"] = "exampletennant"
        
        # xc_vars_dict[dns_name]["gtm_dns_lb"] = bigip_gtm_dict[dns_name]["wideip a"]["pools"]
        xc_vars_dict[dns_name]["xc_dns_lb"] = {}
        xc_vars_dict[dns_name]["xc_dns_lb_name"] = ""
        
        # Currently selecting on wide ip a type only
        xc_vars_dict[dns_name]["gtm_dns_pools"] = bigip_gtm_dict[dns_name]["wideip a"]["pools"]
        xc_vars_dict[dns_name]["gtm_dns_pool_name"] = ""
        xc_vars_dict[dns_name]["dns_type"] = "A"
        xc_vars_dict[dns_name]["xc_dns_type"] = "a_pool"
        xc_vars_dict[dns_name]["xc_dns_pools"] = {}
        # Prepare for monitor variables
        xc_vars_dict[dns_name]["gtm_has_monitor"] = False
        xc_vars_dict[dns_name]["gtm_dns_pool_monitor"] = {}
        xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"] = []
        # Selected Server Monitor
        xc_vars_dict[dns_name]["gtm_server_monitor"] = {}
        xc_vars_dict[dns_name]["gtm_vserver_monitor"] = {}
        # Saved record of old 1
        xc_vars_dict[dns_name]["gtm_server1_monitor"] = {}
        xc_vars_dict[dns_name]["gtm_vserver1_monitor"] = {}
        # Saved record of old 2
        xc_vars_dict[dns_name]["gtm_server2_monitor"] = {}
        xc_vars_dict[dns_name]["gtm_vserver2_monitor"] = {}
        # New XC Monitor
        xc_vars_dict[dns_name]["xc_pool_monitor"] = {}


        # Add logic for short dns name
        dns_tuple = make_dns_name_short(xc_vars_dict[dns_name]["gtm_dns_name"])
        xc_vars_dict[dns_name]["dns_short_name"] = dns_tuple[0]
        xc_vars_dict[dns_name]["gtm_dns_domain_name"] = dns_tuple[1]
        # print(dns_tuple)
        # print(xc_vars_dict[dns_name]["dns_short_name"])
        # print(xc_vars_dict[dns_name]["gtm_dns_domain_name"])

        # TODO: Custom hard coded domains - come back to improve
        # Convert Domain as needed
        if xc_vars_dict[dns_name]["gtm_dns_domain_name"] == "example.com":
            xc_vars_dict[dns_name]["xc_dns_domain_name"] = "new.example.com"
        elif xc_vars_dict[dns_name]["gtm_dns_domain_name"] == "gslb.example.com":
            xc_vars_dict[dns_name]["xc_dns_domain_name"] = "newgslb.example.com"
        else:
            print("DNS DOMAIN Unexpected: '")
            print(xc_vars_dict[dns_name]["gtm_dns_domain_name"])
            print("'")

        # Update xc_dns_name with new domain
        xc_vars_dict[dns_name]["xc_dns_name"] = str(xc_vars_dict[dns_name]["dns_short_name"])+"."+str(xc_vars_dict[dns_name]["xc_dns_domain_name"])
        # print(xc_vars_dict[dns_name]["xc_dns_name"])

        # Create name for new XC LB based on dns name but with '-' instead of '.'
        xc_vars_dict[dns_name]["xc_dns_lb_name"] = str.replace(xc_vars_dict[dns_name]["xc_dns_name"], ".", "-")

        # Build Pools
        # Lookup pool to /Common/ from name
        for pool in xc_vars_dict[dns_name]["gtm_dns_pools"]:
            # Confirm first pool by looking up order 0
            if xc_vars_dict[dns_name]["gtm_dns_pools"][pool]["order"] == "0":
                # Confirm /Common/ needs to be removed
                if pool[0:8] == "/Common/":
                    # Remove /Common/ from the name and save as dictionary entry
                    xc_vars_dict[dns_name]["gtm_dns_pool_name"] = pool[8:]
            # Flag if more than 1 pool present as logic does not yet deal with this
            else:
                print(f"{{WARNING: More than 1 pool ignored in: {xc_vars_dict[dns_name]["gtm_dns_pools"]}}}")
        # Update Pool Reference
        xc_vars_dict[dns_name]["gtm_dns_primary_pool"] = bigip_gtm_dict[xc_vars_dict[dns_name]["gtm_dns_pool_name"]]["pool"]
        # print(xc_vars_dict[dns_name]["gtm_dns_primary_pool"])

        # Create name for new XC LB Orign Pool Name based on GTM DNS Pool name but with '-' instead of '.'
        xc_vars_dict[dns_name]["xc_dns_pool_name"] = str.replace(xc_vars_dict[dns_name]["gtm_dns_pool_name"], ".", "-")

        # Check for Fallback IP - Record/Warn if not set in GTM
        try:
            if xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["fallback-mode"] == "fallback-ip":
                # xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["fallback-ip"]
                pass
            # xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["fallback-ip"]
            else:
                # Catch when Mode Fallback IP but no Fallback IP Set
                # print(f"{{WARNING: No Fallback IP Set For: {xc_vars_dict[dns_name]["global_dns_name"]}}}")
                list_of_dns_pools_gtm_no_fallback.append(xc_vars_dict[dns_name]["global_dns_name"])
        except KeyError:
            # Catch when no Mode Fallback IP
            # print(xc_vars_dict[dns_name]["gtm_dns_primary_pool"])
            # print(f"{{WARNING: No Fallback Set For: {xc_vars_dict[dns_name]["global_dns_name"]}}}")
            list_of_dns_pools_gtm_no_fallback.append(xc_vars_dict[dns_name]["global_dns_name"])

        # Check for LB Method - Record if not set to Global Availability aka F5 DC Priority
        try:
            if xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["load-balancing-mode"] == "global-availability":
                # xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["fallback-ip"]
                xc_vars_dict[dns_name]["xc_dns_lb_method"] = "PRIORITY"
                pass
            else:
                # Catch when Mode Not Set
                list_of_dns_pools_gtm_not_ga_priority_lb_mode.append(xc_vars_dict[dns_name]["global_dns_name"])
        except KeyError:
            # Catch when no Mode Not Set
            list_of_dns_pools_gtm_not_ga_priority_lb_mode.append(xc_vars_dict[dns_name]["global_dns_name"])

        # Record DC Priority Order
        counting_pool_members = 0
        
        # number_of_pool_members = len(xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"])
        # current_member_number = None
        last_member_number = 0
        
        try:
            for member in xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"]:
                
                # if xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"][member]["member-order"] == "0":
                #     print(f"{{MACTCH1: {xc_vars_dict[dns_name]["global_dns_name"]}}}")
                #     pass
                # elif xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"][member]["member-order"] == "1":
                #     pass
                #     print(f"{{MACTCH2: {xc_vars_dict[dns_name]["global_dns_name"]}}}")

                if counting_pool_members < 2:
                    current_member_number = xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"][member]["member-order"]
                    
                    dc_name = clip_dc_name(member)
                    if dc_name == "NOTFOUND":
                        # print(member)
                        # Follow deep dig for dc_name
                        dc_name = dig_for_dc_name(member)

                    if last_member_number:
                        if current_member_number > last_member_number:
                            # Put second member in slot 2
                            xc_vars_dict[dns_name]["dc_secondary"] = dc_name
                            xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_name"] = member
                            #print(xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_name"])
                        else:
                            # Catch and swap old member 1 to slot 2
                            xc_vars_dict[dns_name]["dc_secondary"] = xc_vars_dict[dns_name]["dc_primary"]
                            xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_name"] = xc_vars_dict[dns_name]["dc_primary_gtm_member_1_name"]
                            # Place new member in slot 1
                            xc_vars_dict[dns_name]["dc_primary"] = dc_name
                            xc_vars_dict[dns_name]["dc_primary_gtm_member_1_name"] = member
                    else:
                        # First member so add to slot 1
                        xc_vars_dict[dns_name]["dc_primary"] = dc_name
                        xc_vars_dict[dns_name]["dc_primary_gtm_member_1_name"] = member
                        # Flag position of member added
                        last_member_number = current_member_number
                    counting_pool_members += 1
                    # print(f"{{MACTCH2: {xc_vars_dict[dns_name]["global_dns_name"]}}}")
                
                # Catch for Edge Case - xxxxxxxx.example.com Specifically - has 3 members and need to ignore first
                elif xc_vars_dict[dns_name]["gtm_dns_pool_name"]:
                    name = xc_vars_dict[dns_name]["gtm_dns_pool_name"]
                    if name == "xxxxxxxx.example.com":
                        # print("catch xxxxxxxx.example.com")
                        for catch_member in xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"]:
                            dc_name = clip_dc_name(catch_member)
                            if dc_name == "NOTFOUND":
                                # print(member)
                                # Follow deep dig for dc_name
                                dc_name = dig_for_dc_name(member)

                            # Ignore 0 - yyyyy.example.com_dc1_ns
                            # if xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"][catch_member]["member-order"] == "0":
                            #     xc_vars_dict[dns_name]["dc_tertiary"] = dc_name
                            #     xc_vars_dict[dns_name]["dc_tertiary_gtm_member_3_name"] = catch_member
                            # Set xxxxxxxx.example.com_dc1
                            if xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"][catch_member]["member-order"] == "1":
                                xc_vars_dict[dns_name]["dc_primary"] = dc_name
                                xc_vars_dict[dns_name]["dc_primary_gtm_member_1_name"] = catch_member
                            # Set xxxxxxxx.example.com_dc2
                            if xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["members"][catch_member]["member-order"] == "2":
                                xc_vars_dict[dns_name]["dc_secondary"] = dc_name
                                xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_name"] = catch_member
                
                else:
                    list_of_dns_pools_gtm_with_unexpected_members.append(xc_vars_dict[dns_name]["global_dns_name"])
                    counting_pool_members += 1
                    print(f"{{WARINING: Ignoring Over 2 Members - {counting_pool_members} seen in Pool: {xc_vars_dict[dns_name]["global_dns_name"]}}}")
        except KeyError:
            # Catch when no Members or Member Order not found
            list_of_dns_pools_gtm_with_unexpected_members.append(xc_vars_dict[dns_name]["global_dns_name"])
            # print(f"{{WARINING: Issue Looking Up Members in Pool: {xc_vars_dict[dns_name]["global_dns_name"]}}}")

        try:
            member_1_server_vserver_name_tuple = seperate_out_server_name(xc_vars_dict[dns_name]["dc_primary_gtm_member_1_name"])
            xc_vars_dict[dns_name]["dc_primary_gtm_member_1_server_name"] = member_1_server_vserver_name_tuple[0]
            xc_vars_dict[dns_name]["dc_primary_gtm_member_1_vserver_name"] = member_1_server_vserver_name_tuple[1]
        except KeyError:
            print(f"{{WARINING: Unable to set Member 1 names: {xc_vars_dict[dns_name]["global_dns_name"]}}}")

        try:
            member_2_present = False
            # Make sure there is a second member first
            try:
                if xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_name"]:
                    member_2_present = True
            except KeyError:
                pass
            
            if member_2_present:
                member_2_server_vserver_name_tuple = seperate_out_server_name(xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_name"])
                xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_server_name"] = member_2_server_vserver_name_tuple[0]
                xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_vserver_name"] = member_2_server_vserver_name_tuple[1]
        except KeyError:
            print(f"{{WARINING: Unable to set Member 2 names: {xc_vars_dict[dns_name]["global_dns_name"]}}}")

        try:
            monitor_name = xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["monitor"]
            
            if monitor_name == "min":
                # Catch and log unsupported monitor
                print(f"{{WARINING: Ignoring MIN Monitor: {xc_vars_dict[dns_name]["global_dns_name"]} setting to TCP }}")
                xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"] = "tcp"
            else:
                # Strip /Common/ out of name
                xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"] = monitor_name[8:]

            try:
                and_additional_monitor = xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["and"]
                print(f"{{WARINING: Ignoring AND Monitor: {xc_vars_dict[dns_name]["global_dns_name"]} of {and_additional_monitor} }}")
            except KeyError:
                pass
            try:
                or_additional_monitor = xc_vars_dict[dns_name]["gtm_dns_primary_pool"]["or"]
                print(f"{{WARINING: Ignoring OR Monitor: {xc_vars_dict[dns_name]["global_dns_name"]} of {or_additional_monitor} }}")
            except KeyError:
                pass

        except KeyError:
            pass
            # print(f"{{WARINING: No Monitor Found: {xc_vars_dict[dns_name]["global_dns_name"]}}}")


        # Verifying Pool Monitors - xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]
        # try:
        #     print(xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"])
        # except KeyError:
        #     print("No monitor")


        # Monitor Section 1 of 3 - Parse First Primary Pool for a Monitor
        try:
            for item in bigip_gtm_dict[xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]]:
                if item == "monitor http":
                    xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["monitor_name"] = xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]
                    xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"].append({"pool_monitor":xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]})
                    for sub_monitor_item in bigip_gtm_dict[xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]][item]:
                        xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["monitor type"] = "http"
                        xc_vars_dict[dns_name]["gtm_dns_pool_monitor"][sub_monitor_item] = bigip_gtm_dict[xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]][item][sub_monitor_item]
                        xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                elif item == "monitor https":
                    xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["monitor_name"] = xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]
                    xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"].append({"pool_monitor":xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]})
                    for sub_monitor_item in bigip_gtm_dict[xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]][item]:
                        xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["monitor type"] = "https"
                        xc_vars_dict[dns_name]["gtm_dns_pool_monitor"][sub_monitor_item] = bigip_gtm_dict[xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]][item][sub_monitor_item]
                        xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                elif item == "monitor tcp":
                    xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["monitor_name"] = xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]
                    xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"].append({"pool_monitor":xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]})
                    for sub_monitor_item in bigip_gtm_dict[xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]][item]:
                        xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["monitor type"] = "tcp"
                        xc_vars_dict[dns_name]["gtm_dns_pool_monitor"][sub_monitor_item] = bigip_gtm_dict[xc_vars_dict[dns_name]["gtm_dns_primary_pool_monitor"]][item][sub_monitor_item]
                        xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                # Catch When no monitor on Pool
                else:
                    print(f"{{WARINING: Ignoring Monitor Type: {xc_vars_dict[dns_name]["global_dns_name"]} of '{item}' }}")
                    # pass
                
        except KeyError:
            # print(f"{{WARINING: No Monitor Primary Pool: {xc_vars_dict[dns_name]["global_dns_name"]} of '{item}' }}")
            pass

        # Monitor Section 2 and 3 - Parse First Primary Pool Server and Vserver for a Monitor
        try:
            
        # Monitor Section 2 - Parse First Primary Pool Server and Vserver for a Monitor

            # Check and Add First Primary Pool Server Monitor
            try:
                if bigip_gtm_dict[xc_vars_dict[dns_name]["dc_primary_gtm_member_1_server_name"]]["server"]["monitor"]:
                    monitor_name = bigip_gtm_dict[xc_vars_dict[dns_name]["dc_primary_gtm_member_1_server_name"]]["server"]["monitor"]
                    # Strip /Common/ out of name and override monitor with new monitor
                    # print("fullname")
                    # print(monitor_name)
                    monitor_name = monitor_name[8:]
                    # print(monitor_name)

                    if monitor_name == "bigip":
                        # Skip if just bigip (device monitor) as not needed
                        pass
                    else:
                        xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor_name"] = monitor_name
                        xc_vars_dict[dns_name]["gtm_server1_monitor"]["monitor_name"] = monitor_name
                        if xc_vars_dict[dns_name]["gtm_has_monitor"]:
                            xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"].append({"server1_monitor":monitor_name})
                            if monitor_name == "gateway_icmp":
                                pass
                            else:
                                # print("recording extra Monitors not 'bigip' or 'icmp' ")
                                pass
                        
                        if monitor_name == "gateway_icmp":
                            # Catch ICMP monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"] = "icmp"
                            xc_vars_dict[dns_name]["gtm_server1_monitor"]["monitor type"] = "icmp"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True

                        else:

                            # First Lookup actual monitor
                            try:
                                for item in bigip_gtm_dict[monitor_name]:
                                    print(bigip_gtm_dict)
                                    print(item)
                                    if item == "monitor http":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"] = "http"
                                            xc_vars_dict[dns_name]["gtm_server_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_server1_monitor"]["monitor type"] = "http"
                                            xc_vars_dict[dns_name]["gtm_server1_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    elif item == "monitor https":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"] = "https"
                                            xc_vars_dict[dns_name]["gtm_server_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_server1_monitor"]["monitor type"] = "https"
                                            xc_vars_dict[dns_name]["gtm_server1_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    elif item == "monitor tcp":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"] = "tcp"
                                            xc_vars_dict[dns_name]["gtm_server_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_server1_monitor"]["monitor type"] = "tcp"
                                            xc_vars_dict[dns_name]["gtm_server1_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    # Catch When no monitor on Pool
                                    else:
                                        print(f"{{WARINING: Ignoring Monitor Type: {xc_vars_dict[dns_name]["global_dns_name"]} of '{item}' }}")
                                        # pass

                            except KeyError:
                                print(f"{{WARINING: Could not key into Monitor: {xc_vars_dict[dns_name]["global_dns_name"]} }}")
                                pass
            except KeyError:
                # print(f"{{WARINING: Lookup Failed Member 1 server monitor: {xc_vars_dict[dns_name]["dc_primary_gtm_member_1_server_name"]} }}")
                pass

            # Check and Add First vServer Monitor
            try:
                if bigip_gtm_dict[xc_vars_dict[dns_name]["dc_primary_gtm_member_1_server_name"]]["server"]["virtual-servers"][xc_vars_dict[dns_name]["dc_primary_gtm_member_1_vserver_name"]]["monitor"]:
                    monitor_name = bigip_gtm_dict[xc_vars_dict[dns_name]["dc_primary_gtm_member_1_server_name"]]["server"]["virtual-servers"][xc_vars_dict[dns_name]["dc_primary_gtm_member_1_vserver_name"]]["monitor"]
                    # Strip /Common/ out of name and override monitor with new monitor
                    #print("fullname")
                    #print(monitor_name)
                    monitor_name = monitor_name[8:]
                    #print(monitor_name)

                    if monitor_name == "bigip":
                        # Skip if just bigip (device monitor) as not needed
                        pass
                    else:
                        xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                        xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor_name"] = monitor_name
                        if xc_vars_dict[dns_name]["gtm_has_monitor"]:
                            xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"].append({"vserver1_monitor":monitor_name})
                                                        
                            if monitor_name == "gateway_icmp":
                                pass
                            else:
                                # print("recording extra Monitors not 'bigip' or 'icmp' ")
                                pass
                        
                        if monitor_name == "gateway_icmp":
                            # Catch ICMP monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "icmp"
                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "icmp"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "http":
                            # Catch Generic HTTP monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http"
                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "http"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "http_head_f5":
                            # Catch Generic HTTP Head (not GET) monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http_head"
                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "http_head"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "https":
                            # Catch Generic HTTPS monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "https"
                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "https"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "https_head_f5":
                            # Catch Generic HTTPS Head (not GET) monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "https_head"
                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "https_head"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "tcp":
                            # Catch Generic TCP monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "tcp"
                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "tcp"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        else:
                            try:
                                for item in bigip_gtm_dict[monitor_name]:
                                    if item == "monitor http":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http"
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "http"
                                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    elif item == "monitor https":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "https"
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "https"
                                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    elif item == "monitor tcp":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "tcp"
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] = "tcp"
                                            xc_vars_dict[dns_name]["gtm_vserver1_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    # Catch When no monitor on Pool
                                    else:
                                        print(f"{{WARINING: Ignoring Monitor Type: {xc_vars_dict[dns_name]["global_dns_name"]} of '{item}' }}")
                                        # pass

                            except KeyError:
                                print(f"{{WARINING: Could not key into Monitor: {xc_vars_dict[dns_name]["global_dns_name"]} Monitor name '{monitor_name}'}}")
                                # pass
                   
            except KeyError:
                # print(f"{{WARINING: Lookup Failed Member 1 vserver monitor: {xc_vars_dict[dns_name]["dc_primary_gtm_member_1_vserver_name"]}}}")
                pass


        # Monitor Section 3 - Parse Secondary Pool Server and Vserver for a Monitor

            # Check and Add Second Primary Pool Server Monitor if needed
            try:
                if bigip_gtm_dict[xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_server_name"]]["server"]["monitor"]:
                    monitor_name = bigip_gtm_dict[xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_server_name"]]["server"]["monitor"]
                    # Strip /Common/ out of name and override monitor with new monitor
                    # print("fullname")
                    # print(monitor_name)
                    monitor_name = monitor_name[8:]
                    # print(monitor_name)

                    if monitor_name == "bigip":
                        # Skip if just bigip (device monitor) as not needed
                        pass
                    
                    else:
                        xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor_name"] = monitor_name
                        xc_vars_dict[dns_name]["gtm_server2_monitor"]["monitor_name"] = monitor_name
                        if xc_vars_dict[dns_name]["gtm_has_monitor"]:
                            xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"].append({"server2_monitor":monitor_name})
                            if monitor_name == "gateway_icmp":
                                pass
                            else:
                                # print("recording extra Monitors not 'bigip' or 'icmp' ")
                                pass
                        
                        
                        if monitor_name == "gateway_icmp":
                            # Catch ICMP monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"] = "icmp"
                            xc_vars_dict[dns_name]["gtm_server2_monitor"]["monitor type"] = "icmp"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True

                        else:

                            # First Lookup actual monitor
                            try:
                                for item in bigip_gtm_dict[monitor_name]:
                                    if item == "monitor http":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"] = "http"
                                            xc_vars_dict[dns_name]["gtm_server_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_server2_monitor"]["monitor type"] = "http"
                                            xc_vars_dict[dns_name]["gtm_server2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    elif item == "monitor https":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"] = "https"
                                            xc_vars_dict[dns_name]["gtm_server_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_server2_monitor"]["monitor type"] = "https"
                                            xc_vars_dict[dns_name]["gtm_server2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    elif item == "monitor tcp":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"] = "tcp"
                                            xc_vars_dict[dns_name]["gtm_server_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_server2_monitor"]["monitor type"] = "tcp"
                                            xc_vars_dict[dns_name]["gtm_server2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    # Catch When no monitor on Pool
                                    else:
                                        print(f"{{WARINING: Ignoring Monitor Type: {xc_vars_dict[dns_name]["global_dns_name"]} of '{item}' }}")
                                        # pass

                            except KeyError:
                                print(f"{{WARINING: Could not key into Monitor: {xc_vars_dict[dns_name]["global_dns_name"]} }}")
                                pass
            except KeyError:
                # print(f"{{WARINING: Lookup Failed Member 2 server monitor: {xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_server_name"]} }}")
                pass

            # Check and Add Second vServer Monitor
            try:
                if bigip_gtm_dict[xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_server_name"]]["server"]["virtual-servers"][xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_vserver_name"]]["monitor"]:
                    monitor_name = bigip_gtm_dict[xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_server_name"]]["server"]["virtual-servers"][xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_vserver_name"]]["monitor"]
                    # Strip /Common/ out of name and override monitor with new monitor
                    #print("fullname")
                    #print(monitor_name)
                    monitor_name = monitor_name[8:]
                    #print(monitor_name)

                    if monitor_name == "bigip":
                        # Skip if just bigip (device monitor) as not needed
                        pass
                    else:
                        # xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                        xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor_name"] = monitor_name
                        if xc_vars_dict[dns_name]["gtm_has_monitor"]:
                            xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"].append({"vserver2_monitor":monitor_name})
                            
                            if monitor_name == "gateway_icmp":
                                pass
                            else:
                                # print("recording extra Monitors not 'bigip' or 'icmp' ")
                                pass
                        
                        if monitor_name == "gateway_icmp":
                            # Catch ICMP monitor not detailed in configs and mark manually
                            try:
                                if xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "icmp"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https_head":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "icmp"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "http":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "icmp"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "http_head":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "icmp"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "tcp":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "icmp"
                                else:
                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "icmp"
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "icmp"
                            except KeyError:
                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "icmp"
                                xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "icmp"
                                xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "http":
                            # Catch Generic HTTP monitor not detailed in configs and mark manually
                            try:
                                if xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https_head":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http"
                                else:
                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http"
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http"
                            except KeyError:
                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http"
                                xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http"
                                xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "http_head_f5":
                            # Catch Generic HTTP Head (not GET) monitor not detailed in configs and mark manually
                            try:
                                if xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http_head"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https_head":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http_head"
                                else:
                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http_head"
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http_head"
                            except KeyError:
                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http_head"
                                xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http_head"
                                xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "https":
                            # Catch Generic HTTPS monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "https"
                            xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "https"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "https_head_f5":
                            # Catch Generic HTTPS Head (not GET) monitor not detailed in configs and mark manually
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "https_head"
                            xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "https_head"
                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        elif monitor_name == "tcp":
                            # Catch Generic TCP monitor not detailed in configs and mark manually
                            try:
                                if xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https_head":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "http":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "http_head":
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                else:
                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "tcp"
                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                            except KeyError:
                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "tcp"
                                xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                        else:
                            try:
                                for item in bigip_gtm_dict[monitor_name]:
                                    if item == "monitor http":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            try:
                                                if xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https":
                                                    # Skip setting selected monitor http over https
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http"
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                else:
                                                    # Otherwise set as normal
                                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http"
                                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http"
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            except KeyError:
                                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "http"
                                                xc_vars_dict[dns_name]["gtm_vserver_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "http"
                                                xc_vars_dict[dns_name]["gtm_vserver2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    elif item == "monitor https":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "https"
                                            xc_vars_dict[dns_name]["gtm_vserver_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "https"
                                            xc_vars_dict[dns_name]["gtm_vserver2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    elif item == "monitor tcp":
                                        for sub_monitor_item in bigip_gtm_dict[monitor_name][item]:
                                            try:
                                                if xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "https":
                                                    # Skip setting selected monitor tcp over https
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                elif xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] == "http":
                                                    # Skip setting selected monitor tcp over http
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                else:
                                                    # Otherwise set as normal
                                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "tcp"
                                                    xc_vars_dict[dns_name]["gtm_vserver_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                                    xc_vars_dict[dns_name]["gtm_vserver2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                            except KeyError:
                                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor_name"] = monitor_name
                                                xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"] = "tcp"
                                                xc_vars_dict[dns_name]["gtm_vserver_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"] = "tcp"
                                                xc_vars_dict[dns_name]["gtm_vserver2_monitor"][sub_monitor_item] = bigip_gtm_dict[monitor_name][item][sub_monitor_item]
                                                xc_vars_dict[dns_name]["gtm_has_monitor"] = True
                                    # Catch When no monitor on Pool
                                    else:
                                        print(f"{{WARINING: Ignoring Monitor Type: {xc_vars_dict[dns_name]["global_dns_name"]} of '{item}' }}")
                                        # pass

                            except KeyError:
                                print(f"{{WARINING: Could not key into Monitor: {xc_vars_dict[dns_name]["global_dns_name"]} }}")
                                # pass
                   
            except KeyError:
                print(f"{{WARINING: Lookup Failed Member 2 vserver monitor: {xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_vserver_name"]}}}")
                # pass

                
        except KeyError:
            print("warning")
            #pass


        # Warn if Monitor Conflict
        try:
            if xc_vars_dict[dns_name]["gtm_server_monitor"]["monitor type"]:
                try:
                    if xc_vars_dict[dns_name]["gtm_server1_monitor"]["monitor type"] == xc_vars_dict[dns_name]["gtm_server2_monitor"]["monitor type"]:
                        pass
                    else:
                        print(f"{{WARINING: Difference in Server 1 and Server 2 Monitors Detected: {xc_vars_dict[dns_name]["global_dns_name"]}}}")
                        # print("Server1")
                        # print(xc_vars_dict[dns_name]["gtm_server1_monitor"])
                        # print("Server2")
                        # print(xc_vars_dict[dns_name]["gtm_server2_monitor"])
                        # print("Selected")
                        # print(xc_vars_dict[dns_name]["gtm_server_monitor"])
                except KeyError:
                    pass

        except KeyError:
            pass
        
        # Try vServer Moniotr
        try:
            if xc_vars_dict[dns_name]["gtm_vserver_monitor"]["monitor type"]:
                try:
                    if xc_vars_dict[dns_name]["gtm_vserver1_monitor"]["monitor type"] == xc_vars_dict[dns_name]["gtm_vserver2_monitor"]["monitor type"]:
                        pass
                    else:
                        print(f"{{WARINING: Difference in vServer 1 and vServer 2 Monitors Detected: {xc_vars_dict[dns_name]["global_dns_name"]}}}")
                        # print("vServer1")
                        # print(xc_vars_dict[dns_name]["gtm_vserver1_monitor"])
                        # print("vServer2")
                        # print(xc_vars_dict[dns_name]["gtm_vserver2_monitor"])
                        # print("Selected")
                        # print(xc_vars_dict[dns_name]["gtm_vserver_monitor"])
                except KeyError:
                    pass

        except KeyError:
            pass


        # Add in general monitor values
        try:
            if xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"]:

                # num_of_old_pools = len(xc_vars_dict[dns_name]["gtm_dns_pool_monitor"]["all_old_monitors"])
                source_monitor_name = find_best_monitor(xc_vars_dict[dns_name])
                source_monitor_type = xc_vars_dict[dns_name][source_monitor_name]["monitor type"]

                if source_monitor_type in ["https", "https_head", "http", "http_head"]:
                    
                    if source_monitor_type in ["https", "https_head"]:
                        xc_vars_dict[dns_name]["xc_pool_monitor"]["monitor type"] = "https"
                    if source_monitor_type in ["http", "http_head"]:
                        xc_vars_dict[dns_name]["xc_pool_monitor"]["monitor type"] = "http"

                    try:
                        xc_vars_dict[dns_name]["xc_pool_monitor"]["send"] = xc_vars_dict[dns_name][source_monitor_name]["send"]
                    except KeyError:
                        # print(f"{{WARINING: No old HTTP String Detected: In {xc_vars_dict[dns_name]["global_dns_name"]} for {xc_vars_dict[dns_name][source_monitor_name]}}}")
                        xc_vars_dict[dns_name]["xc_pool_monitor"]["send"] = "DEFAULT"
                    try:
                        xc_vars_dict[dns_name]["xc_pool_monitor"]["recv"] = xc_vars_dict[dns_name][source_monitor_name]["recv"]
                    except KeyError:
                        # print(f"{{WARINING: No old HTTP Receive String Detected: In {xc_vars_dict[dns_name]["global_dns_name"]} for {xc_vars_dict[dns_name][source_monitor_name]}}}")
                        xc_vars_dict[dns_name]["xc_pool_monitor"]["recv"] = "DEFAULT"
                    try:
                        xc_vars_dict[dns_name]["xc_pool_monitor"]["description"] = xc_vars_dict[dns_name][source_monitor_name]["description"]
                    except KeyError:
                        # print(f"{{WARINING: No old HTTP description Detected: In {xc_vars_dict[dns_name]["global_dns_name"]} for {xc_vars_dict[dns_name][source_monitor_name]}}}")
                        xc_vars_dict[dns_name]["xc_pool_monitor"]["description"] = ""

                elif source_monitor_type in ["tcp"]:
                    # Nothing to add at currently as all use default tcp values
                    pass
                elif source_monitor_type in ["icmp"]:
                    # Nothing to add at currently as all use default icmp values
                    pass
                else:
                    print("WARNING: Unable to find and build source monitor")

                try:
                    # Create name for new XC Monitor name based on source monitor name but with '-' instead of '.'
                    xc_vars_dict[dns_name]["xc_pool_monitor"]["monitor_name"] = str.replace(xc_vars_dict[dns_name][source_monitor_name]["monitor_name"], ".", "-")
                except KeyError:
                    print(f"{{ST WARINING: No Old Monitors Found: source {source_monitor_name} and {xc_vars_dict[dns_name]["global_dns_name"]} in {xc_vars_dict[dns_name][source_monitor_name]}}}")

        except KeyError:
            print(f"{{WARINING: No Old Monitors Found: source {source_monitor_name} and {xc_vars_dict[dns_name]["global_dns_name"]} in {xc_vars_dict[dns_name][source_monitor_name]}}}")
            #pass
        

        # TODO: Key in specific changes / manipulation of monitor vlaues as needed


        # Key in IPs and Description for XC use
        try:
            pass

            server = xc_vars_dict[dns_name]["dc_primary_gtm_member_1_server_name"]
            vserver = xc_vars_dict[dns_name]["dc_primary_gtm_member_1_vserver_name"]
            ip_port = bigip_gtm_dict[server]["server"]["virtual-servers"][vserver]["destination"]
            ip_only_tuple = ip_port.split(":")
            # ip_only = ip_only_tuple[0]
            xc_vars_dict[dns_name]["dc_primary_gtm_member_1_ip"] = ip_only_tuple[0]


            ## xc_vars_dict[dns_name]["dc_primary_gtm_member_1_name"]
            # xc_vars_dict[dns_name]["dc_primary_gtm_member_1_server_name"]
            # xc_vars_dict[dns_name]["dc_primary_gtm_member_1_vserver_name"]
            ## xc_vars_dict[dns_name]["dc_primary_gtm_member_1_ip"]
            ## xc_vars_dict[dns_name]["dc_primary_gtm_member_1_description"]

            server = xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_server_name"]
            vserver = xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_vserver_name"]
            ip_port = bigip_gtm_dict[server]["server"]["virtual-servers"][vserver]["destination"]
            ip_only_tuple = ip_port.split(":")
            # ip_only = ip_only_tuple[0]
            xc_vars_dict[dns_name]["dc_secondary_gtm_member_2_ip"] = ip_only_tuple[0]

        except KeyError:
            print(f"{{WARINING: Issue adding member IPs: {xc_vars_dict[dns_name]["global_dns_name"]} }}")
            #pass

        
    # FINAL SECTION OF FUNCTION - ALL FINISHED WITH INITIAL DICTIONARY 'xc_vars_dict' BUILDING

    # Swap monitor names - If required

    # Bring in Monitor SWAP list
    try:
        monitor_swaps_dict = {}
        
        with open('list_of_monitor_name_swaps.csv', 'r') as csv_vars_file:
            csv_file = csv.DictReader(csv_vars_file)
            for row in csv_file:
                # Create an old/new dictionary
                monitor_swaps_dict[row['old_monitor_name']] = row['new_monitor_name']
        # print(dns_names_to_skip)
    except FileNotFoundError:
        print("Unable to find Monitor Name Swap List - No DNS Monitor Names Swapped")
    
    # Swap Moniotor names
    for dns_name in xc_vars_dict:
        try:
            old_monitor_name = xc_vars_dict[dns_name]["xc_pool_monitor"]["monitor_name"]
            new_monitor_name = monitor_swaps_dict[old_monitor_name]
            xc_vars_dict[dns_name]["xc_pool_monitor"]["monitor_name"] = new_monitor_name
            # print(f"{{Found {old_monitor_name} and swapped with {new_monitor_name} On {xc_vars_dict[dns_name]["global_dns_name"]} }}")
        except KeyError:
            pass

    # Bring in DNS Zone RRSET Name List
    try:
        rr_names_dict = {}
        
        with open('list_of_dns_zone_rr_names.csv', 'r') as csv_vars_file:
            csv_file = csv.DictReader(csv_vars_file)
            for row in csv_file:
                # Create an old/new dictionary
                rr_names_dict[row['dns_short_name']] = row['dns_zone_rrset_name']
        # print(dns_names_to_skip)
    except FileNotFoundError:
        print("Unable to find DNS Zone RR Names List - No DNS RR Names Added")
    
    # Add RR names
    for dns_name in xc_vars_dict:
        try:
            short_dns_name = xc_vars_dict[dns_name]["dns_short_name"]
            try:
                new_rrset_name = rr_names_dict[short_dns_name]
                xc_vars_dict[dns_name]["xc_rrset_name"] = new_rrset_name
                # print(f"{{Found {short_dns_name} and added {new_rrset_name} as RRSET}}")
            except KeyError:
                pass
                # print(f"{{No RRSET Found for {short_dns_name}}}")
        except KeyError:
            pass

    # Check for any unexpected values in send/receive strings - clean up csv output by replacing DEFAULT
    for dns_name in xc_vars_dict:
        try:
            if xc_vars_dict[dns_name]["xc_pool_monitor"]["monitor_name"] == "https-v1v2v3-200-ok-443":
                xc_vars_dict[dns_name]["xc_pool_monitor"]["send"] = "HEAD / HTTP/1.0\\r\\nUser-Agent: F5DC-DNSLB-Healthcheck\\r\\n\\r\\n"
                xc_vars_dict[dns_name]["xc_pool_monitor"]["recv"] = "^HTTP\\/[1-3](\\.[0-1])? 200 OK"
            elif xc_vars_dict[dns_name]["xc_pool_monitor"]["monitor_name"] == "post-api-https":
                xc_vars_dict[dns_name]["xc_pool_monitor"]["send"] = "POST /api/ping/anonymous HTTP/1.1\\r\\nHost: fqdn\\r\\nContent-Length: 0\\r\\nUser-Agent: F5DC-DNSLB-Healthcheck\\r\\nConnection: Close\\r\\n\\r\\n"
                xc_vars_dict[dns_name]["xc_pool_monitor"]["recv"] = "^HTTP\\/[1-3](\\.[0-1])? 200 OK"
            elif xc_vars_dict[dns_name]["xc_pool_monitor"]["monitor_name"] == "http-2xx-or-4xx":
                xc_vars_dict[dns_name]["xc_pool_monitor"]["send"] = "HEAD / HTTP/1.1\\r\\nHost: fqdn\\r\\nUser-Agent: F5DC-DNSLB-Healthcheck\\r\\nConnection: Close\\r\\n\\r\\n"
                xc_vars_dict[dns_name]["xc_pool_monitor"]["recv"] = "^HTTP\\/[1-3](\\.[0-1])? (2\\d{2}|4\\d{2})"
            else:
                if xc_vars_dict[dns_name]["xc_pool_monitor"]["send"] == "DEFAULT":
                    print(f"{{WARNING: DEFAULT found but not expected for Monitor value on {xc_vars_dict[dns_name]["global_dns_name"]} }}")
                if xc_vars_dict[dns_name]["xc_pool_monitor"]["recv"] == "DEFAULT":
                    print(f"{{WARNING: DEFAULT found but not expected for Monitor value on {xc_vars_dict[dns_name]["global_dns_name"]} }}")
        except KeyError:
            pass
    
    # Check for HTTP recive strings (recv) that are "none" - match "recv-status-code": "404" and update
    for dns_name in xc_vars_dict:
        try:
            if xc_vars_dict[dns_name]["xc_pool_monitor"]["recv"] == "none":
                xc_vars_dict[dns_name]["xc_pool_monitor"]["recv"] = "^HTTP\\/[1-3](\\.[0-1])? (2\\d{2}|4\\d{2})"
                # if xc_vars_dict[dns_name]["xc_pool_monitor"]["recv-status-code"] == "404":
                #     print(f"{{Found and Repalced 404 with Any 2xx and 4xx on {xc_vars_dict[dns_name]["global_dns_name"]} }}")
                # else: 
                #     print(f"{{Updated recv string but was not a 404 limited before on {xc_vars_dict[dns_name]["global_dns_name"]} }}")
                old_send = xc_vars_dict[dns_name]["xc_pool_monitor"]["send"]
                if old_send[0:3] == "GET":
                    xc_vars_dict[dns_name]["xc_pool_monitor"]["send"] = "HEAD" + old_send[3:]
        except KeyError:
            pass

    


    # Bring in trim list
    try:
        dns_names_to_skip = []
        
        with open('list_of_dns_names_to_skip.csv', 'r') as csv_vars_file:
            csv_file = csv.DictReader(csv_vars_file)
            for row in csv_file:
                # Create an old/new dictionary
                dns_names_to_skip.append(row['HEADER_DNS_NAMES_TO_SKIP'])
        # print(dns_names_to_skip)
    except FileNotFoundError:
        print("Unable to find Trim List - No DNS Names Skipped")

    # Convert GTM dict to nice indent format
    # bigip_gtm_dict_json_string = json.dumps(bigip_gtm_dict, indent=4)
    # print(bigip_gtm_dict_json_string)
    
    # print(list_of_dns_lb_names)
    # print(xc_vars_dict)
    # Convert to nice indent format
    # xc_vars_dict_json_string = json.dumps(xc_vars_dict, indent=4)
    # print(xc_vars_dict_json_string)

    # Save_a_converted_json
    xc_vars_dict_json_string = json.dumps(xc_vars_dict, indent=4)
    # print(json_string)
    with open('xc_vars_dict' + '_converted.json', 'w') as input_file:
        input_file.write(xc_vars_dict_json_string + "\n")


    # Created Trimmed Dictionary (skip DNS names to be ignored)
    xc_vars_trimmed_dict = {}
    for dns_entry in xc_vars_dict:
        if xc_vars_dict[dns_entry]["global_dns_name"] in dns_names_to_skip:
            # Name in skip list - do nothing
            pass
        else:
            # Namie not in skip list - add to new trimmed dictionary
            xc_vars_trimmed_dict[dns_entry] = xc_vars_dict[dns_entry]

    # Save_a_converted_json_after_trim
    xc_vars_trimmed_dict_json_string = json.dumps(xc_vars_trimmed_dict, indent=4)
    # print(json_string)
    with open('xc_vars_dict' + '_converted_trimmed.json', 'w') as input_file:
        input_file.write(xc_vars_trimmed_dict_json_string + "\n")

    # Create CSV from entire conversion
    # save_xc_ready_csvfile(xc_vars_dict)
    # Create CSV from trimmed conversion
    save_xc_ready_csvfile(xc_vars_trimmed_dict)

    # Generate all JSON files for delivery to F5 Cloud Using Jinja2
    generate_api_files_with_jinja2(xc_vars_trimmed_dict)

    # Generate all JSON files for delivery to F5 Cloud - Create the JSON files directly
    # generate_xc_api_json_files(xc_vars_trimmed_dict)

def generate_xc_api_json_files(xc_vars_dict:dict) -> None:
    pass

    # TODO: Make JSON File

def generate_api_files_with_jinja2(xc_vars_dict:dict) -> None:

    xc_jinja2_dict = {}


    for entry in xc_vars_dict:
        xc_jinja2_dict[entry] = {}
        # Set long_tennat_id
        xc_jinja2_dict[entry]["long_tennat_id"] = xc_vars_dict[entry]["xc_long_tennat_id"]
        # Set short_tennat_id
        xc_jinja2_dict[entry]["short_tennat_id"] = xc_vars_dict[entry]["xc_short_tennat_id"]
        # xc_jinja2_dict[entry]["global_dns_name"] = xc_vars_dict[entry]["global_dns_name"]
        xc_jinja2_dict[entry]["gtm_dns_name"] = xc_vars_dict[entry]["gtm_dns_name"]
        xc_jinja2_dict[entry]["xc_dns_name"] = xc_vars_dict[entry]["xc_dns_name"]
        xc_jinja2_dict[entry]["xc_dns_zone_name"] = xc_vars_dict[entry]["xc_dns_zone_name"]
        # dns_zone_rr_record_name
        xc_jinja2_dict[entry]["dns_zone_rr_record_name"] = xc_vars_dict[entry]["dns_short_name"]
        xc_jinja2_dict[entry]["gtm_dns_domain_name"] = xc_vars_dict[entry]["gtm_dns_domain_name"]
        xc_jinja2_dict[entry]["xc_dns_domain_name"] = xc_vars_dict[entry]["xc_dns_domain_name"]
        # Set dns_zone_rr_group
        xc_jinja2_dict[entry]["dns_zone_rr_group"] = xc_vars_dict[entry]["xc_rrset_name"]
        # Set dnslb_instance_name
        xc_jinja2_dict[entry]["dnslb_instance_name"] = xc_vars_dict[entry]["xc_dns_lb_name"]
        # Set dnslb_pool_type
        xc_jinja2_dict[entry]["dnslb_pool_type"] = xc_vars_dict[entry]["xc_dns_type"]
        # set dnslb_pool_name
        xc_jinja2_dict[entry]["dnslb_pool_name"] = xc_vars_dict[entry]["xc_dns_pool_name"]
        try:
            xc_jinja2_dict[entry]["xc_dns_lb_method"] = xc_vars_dict[entry]["xc_dns_lb_method"]
        except KeyError:
            print(f"{{ERROR - Unable to find xc_dns_lb_method for {xc_vars_dict[entry]["gtm_dns_name"]} }}")
            xc_jinja2_dict[entry]["xc_dns_lb_method"] = "PRIORITY"
        xc_jinja2_dict[entry]["dc_primary"] = xc_vars_dict[entry]["dc_primary"]
        # Set dnslb_pool_member_1_ip
        xc_jinja2_dict[entry]["dnslb_pool_member_1_ip"] = xc_vars_dict[entry]["dc_primary_gtm_member_1_ip"]
        xc_jinja2_dict[entry]["dc_secondary"] = xc_vars_dict[entry]["dc_secondary"]
        # set dnslb_pool_member_2_ip
        xc_jinja2_dict[entry]["dnslb_pool_member_2_ip"] = xc_vars_dict[entry]["dc_secondary_gtm_member_2_ip"]
        # set dnslb_healthcheck_name
        xc_jinja2_dict[entry]["dnslb_healthcheck_name"] = xc_vars_dict[entry]["xc_pool_monitor"]["monitor_name"]
        # Set dnslb_healthcheck_http_send_string
        try:
            send_string_pre_json = xc_vars_dict[entry]["xc_pool_monitor"]["send"]
            # Ensure string is in json format
            send_string_json_ready = json.dumps(send_string_pre_json)
            # Remove start and end "{}" from the string and set
            length_of_send_string = len(send_string_json_ready)
            xc_jinja2_dict[entry]["dnslb_healthcheck_http_send_string"] = send_string_json_ready[1:length_of_send_string-1]
        except KeyError:
            xc_jinja2_dict[entry]["dnslb_healthcheck_http_send_string"] = ""
        # Set dnslb_healthcheck_http_receive_string
        try:
            recv_string_pre_json = xc_vars_dict[entry]["xc_pool_monitor"]["recv"]
            # Ensure string is in json format
            recv_string_json_ready = json.dumps(recv_string_pre_json)
            # Remove start and end "{}" from the string and set
            length_of_recv_string = len(recv_string_json_ready)
            xc_jinja2_dict[entry]["dnslb_healthcheck_http_receive_string"] = recv_string_json_ready[1:length_of_recv_string-1]
        except KeyError:
            xc_jinja2_dict[entry]["dnslb_healthcheck_http_receive_string"] = ""
        # Set dnslb_healthcheck_description
        try:
            xc_jinja2_dict[entry]["dnslb_healthcheck_description"] = xc_vars_dict[entry]["xc_pool_monitor"]["description"]
        except KeyError:
            xc_jinja2_dict[entry]["dnslb_healthcheck_description"] = ""
        try:
            xc_jinja2_dict[entry]["xc_pool_monitor__monitor_type"] = xc_vars_dict[entry]["xc_pool_monitor"]["monitor type"]
        except KeyError:
            xc_jinja2_dict[entry]["xc_pool_monitor__monitor_type"] = ""

    jinja_dns_list = []
    for dns_name in xc_jinja2_dict:
        jinja_dns_list.append(xc_jinja2_dict[dns_name])


    # Healthcheck Template Filling
    environment = Environment(loader=FileSystemLoader("xc_api_templates/1_healthcheck"))
    template = environment.get_template("template_healthcheck.jinja2")
    for dns_name in jinja_dns_list:
        filename = f"{dns_name['dnslb_healthcheck_name'].lower()}.json"
        content = template.render(dns_name)
        with open("jinja_rendered/1_healthcheck/"+filename, mode="w", encoding="utf-8") as rendered_json:
            rendered_json.write(content)
            # print(f"... wrote {filename}")

    # Pool Primary Template Filling
    environment = Environment(loader=FileSystemLoader("xc_api_templates/2_pool"))
    template = environment.get_template("template_pool.jinja2")
    for dns_name in jinja_dns_list:
        filename = f"{dns_name['dnslb_pool_name'].lower()}.json"
        content = template.render(dns_name)
        with open("jinja_rendered/2_pool/"+filename, mode="w", encoding="utf-8") as rendered_json:
            rendered_json.write(content)
            # print(f"... wrote {filename}")

    # Pool Primary Secondary Template Filling
    environment = Environment(loader=FileSystemLoader("xc_api_templates/2_pool"))
    template = environment.get_template("template_pool_fallback.jinja2")
    for dns_name in jinja_dns_list:
        filename = f"{dns_name['dnslb_pool_name'].lower()}_fallback.json"
        content = template.render(dns_name)
        with open("jinja_rendered/2_pool/"+filename, mode="w", encoding="utf-8") as rendered_json:
            rendered_json.write(content)
            # print(f"... wrote {filename}")

    # LB Template Filling
    environment = Environment(loader=FileSystemLoader("xc_api_templates/3_dnslb"))
    template = environment.get_template("template_dnslb.jinja2")
    for dns_name in jinja_dns_list:
        filename = f"{dns_name['dnslb_instance_name'].lower()}.json"
        content = template.render(dns_name)
        with open("jinja_rendered/3_dnslb/"+filename, mode="w", encoding="utf-8") as rendered_json:
            rendered_json.write(content)
            # print(f"... wrote {filename}")

    # DNS Records Template Filling
    environment = Environment(loader=FileSystemLoader("xc_api_templates/4_records"))
    template = environment.get_template("template_dns_record.jinja2")
    for dns_name in jinja_dns_list:
        # print(dns_name['dns_short_name'])
        # print(dns_name['dnslb_healthcheck_name'].lower())
        filename = f"{dns_name['dns_zone_rr_record_name'].lower()}.json"
        content = template.render(dns_name)
        with open("jinja_rendered/4_records/"+filename, mode="w", encoding="utf-8") as rendered_json:
            rendered_json.write(content)
            # print(f"... wrote {filename}")



def save_xc_ready_csvfile(xc_ready_dictionary:dict) -> None:
    """
    Function to take a dictionary ready to go xc_conversion and save out as a csv file
    Writes to xc_vars_dict_converted.csv
    """

    xc_csv_dict = {}

    for entry in xc_ready_dictionary:
        xc_csv_dict[entry] = {}
        # xc_csv_dict[entry]["global_dns_name"] = xc_ready_dictionary[entry]["global_dns_name"]
        xc_csv_dict[entry]["gtm_dns_name"] = xc_ready_dictionary[entry]["gtm_dns_name"]
        xc_csv_dict[entry]["xc_dns_name"] = xc_ready_dictionary[entry]["xc_dns_name"]
        xc_csv_dict[entry]["dns_short_name"] = xc_ready_dictionary[entry]["dns_short_name"]
        xc_csv_dict[entry]["gtm_dns_domain_name"] = xc_ready_dictionary[entry]["gtm_dns_domain_name"]
        xc_csv_dict[entry]["xc_dns_domain_name"] = xc_ready_dictionary[entry]["xc_dns_domain_name"]
        xc_csv_dict[entry]["xc_dns_zone_name"] = xc_ready_dictionary[entry]["xc_dns_zone_name"]
        xc_csv_dict[entry]["xc_rrset_name"] = xc_ready_dictionary[entry]["xc_rrset_name"]
        xc_csv_dict[entry]["xc_dns_lb_name"] = xc_ready_dictionary[entry]["xc_dns_lb_name"]
        xc_csv_dict[entry]["dns_type"] = xc_ready_dictionary[entry]["dns_type"]
        xc_csv_dict[entry]["xc_dns_pool_name"] = xc_ready_dictionary[entry]["xc_dns_pool_name"]
        try:
            xc_csv_dict[entry]["xc_dns_lb_method"] = xc_ready_dictionary[entry]["xc_dns_lb_method"]
        except KeyError:
            print(f"{{ERROR - Unable to find xc_dns_lb_method for {xc_ready_dictionary[entry]["gtm_dns_name"]} }}")
            xc_csv_dict[entry]["xc_dns_lb_method"] = "PRIORITY"
        xc_csv_dict[entry]["dc_primary"] = xc_ready_dictionary[entry]["dc_primary"]
        xc_csv_dict[entry]["dc_primary_gtm_member_1_ip"] = xc_ready_dictionary[entry]["dc_primary_gtm_member_1_ip"]
        xc_csv_dict[entry]["dc_secondary"] = xc_ready_dictionary[entry]["dc_secondary"]
        xc_csv_dict[entry]["dc_secondary_gtm_member_2_ip"] = xc_ready_dictionary[entry]["dc_secondary_gtm_member_2_ip"]
        xc_csv_dict[entry]["xc_pool_monitor__monitor_name"] = xc_ready_dictionary[entry]["xc_pool_monitor"]["monitor_name"]
        try:
            xc_csv_dict[entry]["xc_pool_monitor__send"] = xc_ready_dictionary[entry]["xc_pool_monitor"]["send"]
        except KeyError:
            xc_csv_dict[entry]["xc_pool_monitor__send"] = ""
        try:
            xc_csv_dict[entry]["xc_pool_monitor__recv"] = xc_ready_dictionary[entry]["xc_pool_monitor"]["recv"]
        except KeyError:
            xc_csv_dict[entry]["xc_pool_monitor__recv"] = ""
        try:
            xc_csv_dict[entry]["xc_pool_monitor__description"] = xc_ready_dictionary[entry]["xc_pool_monitor"]["description"]
        except KeyError:
            xc_csv_dict[entry]["xc_pool_monitor__description"] = ""
        try:
            xc_csv_dict[entry]["xc_pool_monitor__monitor_type"] = xc_ready_dictionary[entry]["xc_pool_monitor"]["monitor type"]
        except KeyError:
            xc_csv_dict[entry]["xc_pool_monitor__monitor_type"] = ""

    csv_fieldnames = \
        ["gtm_dns_name","xc_dns_name","dns_short_name","gtm_dns_domain_name","xc_dns_domain_name","xc_dns_zone_name","xc_rrset_name",
         "xc_dns_lb_name","dns_type","xc_dns_pool_name","xc_dns_lb_method",
         "dc_primary","dc_primary_gtm_member_1_ip",
         "dc_secondary","dc_secondary_gtm_member_2_ip",
         "xc_pool_monitor__monitor_name","xc_pool_monitor__send","xc_pool_monitor__recv","xc_pool_monitor__description","xc_pool_monitor__monitor_type"]

    # Build headers like this
    # csv_fieldnames = ["monitor_name" ,"description", "send" , "recv" ,"monitor type"]
    # Build Dictionary table like this
    # xc_csv_dict = {"x":{"monitor_name":"ok","send":"GET /","recv":"200 OK","description":"","monitor type":"https"},"y":{"monitor_name":"oky","send":"GET /y","recv":"200 OKy","description":"y","monitor type":"httpsy"}}

    # Write out to csv File by keying in on dictionary header names
    with open('xc_vars_dict' + '_converted.csv', 'w', newline='') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=csv_fieldnames)
        writer.writeheader()
        for item in xc_csv_dict:
            writer.writerow(xc_csv_dict[item])

# May break out logic of finding best monitor
def find_best_monitor(source_with_monitors_to_parse:dict) -> str:
    """
    Takes dictionary of gtm dns entry , ranks and returns best monitor to use.
    Rank is based on priority (1 is highest ranked)
    6:"icmp",5:"tcp",4:"http",3:"http_head",2:"https_head",1:"https"
    
    Will return a single string of best ranked monitor in form of:
    - gtm_dns_pool_monitor
    - gtm_server_monitor
    - gtm_vserver_monitor

    Or will raise NameError.
    """

    best_pool = ""

    ranked_list_of_monitors = {6:"icmp",5:"tcp",4:"http",3:"http_head",2:"https_head",1:"https"}

    try:
        old_pool_type = source_with_monitors_to_parse["gtm_dns_pool_monitor"]["monitor type"]
        best_pool = "old_pool"
    except KeyError:
        old_pool_type = "not_present"

    try:
        old_server_type = source_with_monitors_to_parse["gtm_server_monitor"]["monitor type"]

        if old_pool_type == "not_present":
            best_pool = "old_server"

        else:
            loop_ranked_list = {}
            for item in ranked_list_of_monitors:
                loop_ranked_list[item] = ranked_list_of_monitors[item]
            list_length = len(ranked_list_of_monitors)
            sorting = True
            while sorting:
                while list_length > 0:
                    list_length -= 1
                    compare = loop_ranked_list.popitem()
                    # print(compare[1])
                    if compare[1] == old_pool_type:
                        best_pool = "old_pool"
                        sorting = False
                    elif compare[1] == old_server_type:
                        best_pool = "old_server"
                        sorting = False
                if sorting:
                    print(f"{{WARNING: Unable to match best pool {compare[1]} and_old_pool {old_pool_type} and_old_server {old_server_type} }}")
                    sorting = False
    except KeyError:
        old_server_type = "not_present"

    try:
        old_vserver_type = source_with_monitors_to_parse["gtm_vserver_monitor"]["monitor type"]

        if old_pool_type == "not_present":
            if old_server_type == "not_present":
                best_pool = "old_vserver"

        elif best_pool == "old_pool":
            loop_ranked_list = {}
            for item in ranked_list_of_monitors:
                loop_ranked_list[item] = ranked_list_of_monitors[item]
            list_length = len(ranked_list_of_monitors)
            sorting = True
            while sorting:
                while list_length > 0:
                    list_length -= 1
                    compare = loop_ranked_list.popitem()
                    # print(compare[1])
                    if compare[1] == old_pool_type:
                        best_pool = "old_pool"
                        sorting = False
                    elif compare[1] == old_vserver_type:
                        best_pool = "old_vserver"
                        sorting = False
                if sorting:
                    print(f"{{WARNING: Unable to match best pool {compare[1]} and_old_pool {old_pool_type} and_old_vserver {old_vserver_type} }}")
                    sorting = False

        elif best_pool == "old_server":
            loop_ranked_list = {}
            for item in ranked_list_of_monitors:
                loop_ranked_list[item] = ranked_list_of_monitors[item]
            list_length = len(ranked_list_of_monitors)
            sorting = True
            while sorting:
                while list_length > 0:
                    list_length -= 1
                    compare = loop_ranked_list.popitem()
                    # print(compare[1])
                    if compare[1] == old_server_type:
                        best_pool = "old_server"
                        sorting = False
                    elif compare[1] == old_vserver_type:
                        best_pool = "old_vserver"
                        sorting = False
                if sorting:
                    print(f"{{WARNING: Unable to match best pool {compare[1]} and_old_server {old_server_type} and_old_vserver {old_vserver_type} }}")
                    sorting = False

        else:
            print("Warning: Unable to rank monitor")
    except KeyError:
        # old_vserver = "not_present"
        pass

    if best_pool == "old_pool":
        return("gtm_dns_pool_monitor")
    elif best_pool == "old_server":
        return("gtm_server_monitor")
    elif best_pool == "old_vserver":
        return("gtm_vserver_monitor")
    else:
        raise NameError("ERROR SORTING FOR BEST POOL")

def make_dns_name_short(long_dns_name:str) -> tuple:
    """
    Takes a dns name and makes it short (removes domain)
    """

    short_name = ""
    domain_name = ""
    host_entry = True
    for letter in long_dns_name:
        if letter == "." and host_entry:
            host_entry = False
        elif host_entry:
            short_name += letter
        else:
            domain_name += letter
    
    # Construct return Tuple
    dns_name_and_domain = (short_name,domain_name)
    return(dns_name_and_domain)

def clip_dc_name(full_objecy_name:str) -> str:

    # Clip DC name
    dc_name_length = len(full_objecy_name)
    # Set DC name based on match
    dc_name = ""

    if full_objecy_name[dc_name_length-3:dc_name_length] == "_dc1":
        dc_name = "dc1"
    elif full_objecy_name[dc_name_length-4:dc_name_length] == "_dc2":
        dc_name = "dc2"
    else:
        # print("No DC Match Found")
        dc_name = "NOTFOUND"
    
    return dc_name


def dig_for_dc_name(full_objecy_name:str) -> str:

    # Clip DC name
    # dc_name_length = len(full_objecy_name)
    # Set DC name based on match
    dc_name = ""

    if full_objecy_name.find("_dc1:") > 0:
        dc_name = "dc1"
    elif full_objecy_name.find("_dc2:") > 0:
        dc_name = "dc2"
    elif full_objecy_name.find("_dc1_") > 0:
        dc_name = "dc1"
    elif full_objecy_name.find("_dc2_") > 0:
        dc_name = "dc2"
    else:
        print("WARNING: No DC Match Found")
        dc_name = "NOTFOUND"

    return dc_name

def seperate_out_server_name(partition_server_colon_vserver:str) -> tuple:
    """
    Takes a gtm server and virtual serer combo and seperate the two.
    Also removes '/Common/' partition header
    Returns TUPLE: (gtm_server_name, gtm_virtual_server_name)
    """

    # Cut /Common/
    server_colon_vserver = partition_server_colon_vserver[8:]
    # Split at :
    server_vserver_split_tuple = server_colon_vserver.split(":")
    # Return Tuple with info
    return(server_vserver_split_tuple)


if __name__ == "__main__":
    # print(sys.argv[1])
    try:
        gtm_conversion_file(sys.argv[1])
    # Catch when file is not parsable UTF 8 or similar
    except UnicodeDecodeError:
        print('Fail to read file - ' + sys.argv[1] + ' : Is this a file to be read?')
    except IndexError:
        gtm_conversion_file()



