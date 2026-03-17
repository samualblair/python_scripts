# Michael W. Johnson - 03-04-2026
# Paring code to parse existing AS3 JSON file and filter or modify information
# This code Specifically provides a function to parse through AS3 JSON and perform tasks and saving in well formatted JSON when done
# One task is to find missing Service Port (member port) information, and add a service port based on Virtual Port (VS Port).

import json
import csv
# import pprint

virtual_port_dict = {}

# in_filename = 'example_good_as3.json'
# in_filename = 'example_bad_as3.json'
# output_filename = 'new_fixed_output.json'
# output_filename = 'new_no_change_output.json'

# TODO: Add tool to convert from 'declaration' from 'non-declaration' formatted json file

def Add_pool_service_port(in_filename) -> None:
    '''
    Parses F5 AS3 JSON File, finds missing member service port information, adds service port based on Virtual Server Port in use, and saves back to the file.
    This is destructive of original file, please backup file prior to running.
    '''

    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        for dec_key in source['declaration']:
            # print(source['declaration'][i])
            try:
                for tenant_key in source['declaration'][dec_key]:
                    try:
                        apps_found = []
                        
                        for application_key in source['declaration'][dec_key][tenant_key]:

                            # Try to find the Current Service Port
                            try:
                                # name_of_application = source['declaration'][dec_key][tenant_key][application_key]
                                class_of_application = source['declaration'][dec_key][tenant_key][application_key]['class']
                                if class_of_application == "Service_HTTP":
                                    apps_found.append(class_of_application)
                                name_of_application_port = source['declaration'][dec_key][tenant_key][application_key]['virtualPort']
                                # print(name_of_application_port)
                                virtual_port_dict['virtualPort_found'] = name_of_application_port
                                # print(apps_found)
                            except KeyError:
                                pass

                            # print(source['declaration'][dec_key][tenant_key][application_key])
                            for app_object_key in source['declaration'][dec_key][tenant_key][application_key]:

                                # Try finding Pool in loop
                                try:
                                    if source['declaration'][dec_key][tenant_key][application_key][app_object_key] == 'Pool':
                                        try:
                                            for member in source['declaration'][dec_key][tenant_key][application_key]['members']:
                                                # null_value = member['servicePort']
                                                pass
                                        except KeyError:
                                            pass
                                            # print("Member has no Service Port - " + str(member))
                                            # current_app = source['declaration'][dec_key][tenant_key]
                                            # print(current_app)
                                            
                                            print("Adding")
                                            for member in source['declaration'][dec_key][tenant_key][application_key]['members']:
                                                member['servicePort'] = virtual_port_dict['virtualPort_found']
                                                # print(member['servicePort'])                                       

                                except TypeError:
                                    pass
                                except KeyError:
                                    pass
                    except TypeError:
                        pass
                    except KeyError:
                        pass
            except TypeError:
                pass
            except KeyError:
                pass
            except Exception as error:
                print(type(error).__name__)
                print(error)



    # output_filename = str(in_filename + '_updated.json')
    output_filename = str(in_filename)

    with open(output_filename, "w") as outfile: 
        json.dump(source, outfile, indent=2)

def Update_vip_ip(in_filename) -> None:
    '''
    Parses F5 AS3 JSON File, and CSV IP old/new file, to swap out old NS VIP IPs with new F5 VIP IPs.
    This is destructive of original file, please backup file prior to running.
    '''

    csv_dic = {}

    with open('old_to_new.csv', 'r') as csv_vars_file:
        csv_file = csv.DictReader(csv_vars_file)
        for row in csv_file:
            # Create an old/new dictionary
            csv_dic[row['old']] = row['new']

    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        for dec_key in source['declaration']:
            # print(source['declaration'][i])
            try:
                for tenant_key in source['declaration'][dec_key]:
                    try:
                        apps_found = []
                        
                        for application_key in source['declaration'][dec_key][tenant_key]:

                            # Try to find the Current Service Port
                            try:
                                # name_of_application = source['declaration'][dec_key][tenant_key][application_key]
                                class_of_application = source['declaration'][dec_key][tenant_key][application_key]['class']
                                
                                # if class_of_application == "Service_HTTP":
                                #     apps_found.append(class_of_application)

                                if class_of_application[0:8] == 'Service_':
                                    # Catch most Service classes with Service Address
                                    if class_of_application != 'Service_Address':
                                        apps_found.append(class_of_application)
                                        try:
                                            name_of_application_ip = source['declaration'][dec_key][tenant_key][application_key]['virtualAddresses']
                                            string_old_ip = 'OLD IP:' + str(source['declaration'][dec_key][tenant_key][application_key]['virtualAddresses'])
                                            #print("Found - Attempting to Swap")
                                            #print(name_of_application_ip + ' and ' + string_old_ip)

                                            # Set the lookup key (first element in list of IPs, assuming only 1 IP aka 1 element)
                                            lookup_key = name_of_application_ip[0]
                                            #print(lookup_key)

                                            # Update the address to the new value, from lookup of old/new dictionary
                                            source['declaration'][dec_key][tenant_key][application_key]['virtualAddresses'] = [ csv_dic[lookup_key] ]
                                            string_new_ip = 'NEW IP:' + str(source['declaration'][dec_key][tenant_key][application_key]['virtualAddresses'])
                                            print(string_old_ip + ' -> ' + string_new_ip)
                                        except KeyError:
                                            # print("Exception on IP VS Service Addresses Swap: " + class_of_application)
                                            pass
                                    # Catch case of dedicated Service Address class
                                    else:
                                        apps_found.append(class_of_application)
                                        try:
                                            name_of_application_ip = source['declaration'][dec_key][tenant_key][application_key]['virtualAddress']
                                            string_old_ip = 'OLD IP:' + str(source['declaration'][dec_key][tenant_key][application_key]['virtualAddress'])
                                            #print("Found - Attempting to Swap")
                                            #print(name_of_application_ip + ' and ' + string_old_ip)

                                            # Set the lookup key (first element in list of IPs, assuming only 1 IP aka 1 element)
                                            lookup_key = name_of_application_ip
                                            #print(lookup_key)

                                            # Update the address to the new value, from lookup of old/new dictionary
                                            source['declaration'][dec_key][tenant_key][application_key]['virtualAddress'] = csv_dic[lookup_key]
                                            # Print message informing update was made
                                            string_new_ip = 'NEW IP:' + str(source['declaration'][dec_key][tenant_key][application_key]['virtualAddress'])
                                            print(string_old_ip + ' -> ' + string_new_ip)
                                        except KeyError:
                                            # print("Exception on IP Service Address: " + class_of_application)
                                            pass

                            except TypeError:
                                pass
                            except KeyError:
                                pass
                    except TypeError:
                        pass
                    except KeyError:
                        pass
            except TypeError:
                pass
            except KeyError:
                pass
            except Exception as error:
                print(type(error).__name__)
                print(error)

    # output_filename = str(in_filename + '_updated.json')
    output_filename = str(in_filename)

    with open(output_filename, "w") as outfile: 
        json.dump(source, outfile, indent=2)

def Update_tenant_name(in_filename) -> None:
    '''
    Parses F5 AS3 JSON File, and CSV IP old/new file, to swap out old Tenant (partition) name.
    This is potentially destructive of original file, please backup file prior to running.
    '''

    destination = {}

    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        for dec_key in source:
            value_of_key = source[dec_key]
            #print(value_of_key)
            destination[dec_key] = value_of_key
        
    # Close source file to prevent dictionary size change error

    # Reopen source file
    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        for dec_key in source['declaration']:
            # print(source['declaration'][i])
            try:
                for tenant_key in source['declaration'][dec_key]:
                    try:
                        # apps_found = []
                        
                        for application_key in source['declaration'][dec_key][tenant_key]:

                            # Try to find the Current Service Port
                            try:
                                #name_of_top_container = source
                                #name_of_declaration_container = source['declaration']
                                #name_of_tenant_container = source['declaration'][dec_key]
                                #name_of_app_container = source['declaration'][dec_key][tenant_key]

                                # Important to keep these as they ensure only running loop inside an application
                                # name_of_application = source['declaration'][dec_key][tenant_key][application_key]
                                # class_of_application = source['declaration'][dec_key][tenant_key][application_key]['class']

                                # TODO: change key from looking for app_ to looking for proper class of an application - "class": "Application"

                                # Check if app name starts with 'app_' or not, only run if it does
                                if 'app_' == tenant_key[0:4]:
                                    # Construct tenant new name, by using app name but replacing (app_) with (t_)
                                    # Current logic loop will do this for all apps, so only last app name remains in tenant name
                                    new_tenant_name = 't_' + tenant_key[4:]
                                    destination['declaration'][new_tenant_name] = source['declaration'][dec_key]
                                    # Only pop the old tenant name if the new tenant name is different - very important check as this loop is only filtering in on application
                                    if not (new_tenant_name == dec_key):
                                        destination['declaration'].pop(dec_key)

                                    # This section replaces app_ with a_ , disabling by default as this is to compressed and not descriptive enough
                                    # # Construct new name app name, by replacing (app_) with (a_)
                                    # new_app_name = 'a_' + tenant_key[4:]
                                    # destination['declaration'][new_tenant_name][new_app_name] = source['declaration'][dec_key][tenant_key]
                                    # # Only pop the old app name if the new app name is different - should not be needed when app name explicitly changing - but leaving here as backup check
                                    # if not (new_app_name == tenant_key):
                                    #     destination['declaration'][new_tenant_name].pop(tenant_key)

                            except TypeError:
                                pass
                            except KeyError:
                                pass
                    except TypeError:
                        pass
                    except KeyError:
                        pass
            except TypeError:
                pass
            except KeyError:
                pass
            except Exception as error:
                print(type(error).__name__)
                print(error)

    # output_filename = str(in_filename + '_updated.json')
    output_filename = str(in_filename)

    with open(output_filename, "w") as outfile: 
        json.dump(destination, outfile, indent=2)

def Update_schema(in_filename) -> None:
    '''
    Parses F5 AS3 JSON File, and CSV IP old/new file, to swap out old schema and schemaVersion.
    This is destructive of original file, please backup file prior to running.
    '''

    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        source['declaration']['schemaVersion'] = "3.54.0"
        source['$schema'] = "https://raw.githubusercontent.com/F5Networks/f5-appsvcs-extension/main/schema/latest/as3-schema.json"

    # output_filename = str(in_filename + '_updated.json')
    output_filename = str(in_filename)

    with open(output_filename, "w") as outfile: 
        json.dump(source, outfile, indent=2)

def Count_vips(in_filename) -> None:
    '''
    Parses F5 AS3 JSON File, Counts IP on VS, Prints output on console
    '''

    count_dic = 0

    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        for dec_key in source['declaration']:
            # print(source['declaration'][i])
            try:
                for tenant_key in source['declaration'][dec_key]:
                    try:
                        for application_key in source['declaration'][dec_key][tenant_key]:
                            # Try to find the Current Service Port
                            try:
                                # name_of_application = source['declaration'][dec_key][tenant_key][application_key]
                                class_of_application = source['declaration'][dec_key][tenant_key][application_key]['class']
                                if class_of_application[0:8] == 'Service_':
                                    if class_of_application != 'Service_Address':
                                        count_dic += 1
                                        #print(class_of_application)
                                        #print(name_of_application)
                            except TypeError:
                                pass
                            except KeyError:
                                pass
                    except TypeError:
                        pass
                    except KeyError:
                        pass
            except TypeError:
                pass
            except KeyError:
                pass
            except Exception as error:
                print(type(error).__name__)
                print(error)
    if __name__ == "__main__":
        print(f'The total number of VS are: {count_dic}')
    else:
        return(count_dic)

def Clean_up_node_names(in_filename) -> None:
    '''
    Parses F5 AS3 JSON File, looks for common issues in Node Names and cleans them up
    This is destructive of original file, please backup file prior to running.
    '''

    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        for dec_key in source['declaration']:
            # print(source['declaration'][i])
            try:
                for tenant_key in source['declaration'][dec_key]:
                    try:
                       
                        for application_key in source['declaration'][dec_key][tenant_key]:

                            # Try to find the Current Service Port
                            try:
                                # name_of_application = source['declaration'][dec_key][tenant_key][application_key]
                                class_of_application = source['declaration'][dec_key][tenant_key][application_key]['class']
                                
                                # if class_of_application == "Service_HTTP":
                                #     apps_found.append(class_of_application)

                                if class_of_application == 'Pool':
                                    # Catch when a Pool
                                    new_pool_members = []
                                    # len_of_pool = len(source['declaration'][dec_key][tenant_key][application_key]['members'])
                                    
                                    for pool_member in source['declaration'][dec_key][tenant_key][application_key]['members']:
                                        # Nothing to do if just IPs - 'serverAddresses' - list of IP strings
                                        # Try when 'servers' - list of objects, with name and address values

                                        #print(pool_member)

                                        new_pool_member_servers = []

                                        try:
                                            for pool_member_server in pool_member['servers']:

                                                #print(pool_member_server)
                                                old_server_name = str(pool_member_server['name'])
                                                #string_old_server_name = 'OLD Node Server Name:' + str(pool_member_server['name'])
                                                #print(string_old_server_name)

                                                string_new_server_name = old_server_name
                                                
                                                # Remove common cases of suffixes/prefixes with Tenant Name (dec_key) or App Name (tenant_key)
                                                string_removal = dec_key + ' '
                                                string_new_server_name = string_new_server_name.removeprefix(string_removal)
                                                string_removal = ' ' + dec_key
                                                string_new_server_name = string_new_server_name.removesuffix(string_removal)
                                                # Catch if name matches other without t_
                                                if len(dec_key) > 2:
                                                     if dec_key[:2] == 't_':
                                                        string_removal = dec_key[2:] + ' '
                                                        string_new_server_name = string_new_server_name.removeprefix(string_removal)
                                                        string_removal = ' ' + dec_key[2:]
                                                        string_new_server_name = string_new_server_name.removesuffix(string_removal)

                                                string_removal = tenant_key + ' '
                                                string_new_server_name = string_new_server_name.removeprefix(string_removal)
                                                string_removal = ' ' + tenant_key
                                                string_new_server_name = string_new_server_name.removesuffix(string_removal)
                                                # Catch if name matches other without app_
                                                if len(tenant_key) > 4:
                                                    if tenant_key[4:] == 'app_':
                                                        string_removal = tenant_key[4:] + ' '
                                                        string_new_server_name = string_new_server_name.removeprefix(string_removal)
                                                        string_removal = ' ' + tenant_key[4:]
                                                        string_new_server_name = string_new_server_name.removesuffix(string_removal)

                                                # TODO: Move or expand this section this number section to some list - maybe an importable csv or something
                                                # Remove common cases of suffixes/prefixes with port numbers
                                                string_new_server_name = string_new_server_name.removesuffix(' 443')
                                                string_new_server_name = string_new_server_name.removesuffix(' 80')
                                                string_new_server_name = string_new_server_name.removesuffix(' 8080')
                                                string_new_server_name = string_new_server_name.removesuffix(' 8443')
                                                string_new_server_name = string_new_server_name.replace(' 443 ','')
                                                string_new_server_name = string_new_server_name.replace(' 80 ','')
                                                string_new_server_name = string_new_server_name.replace(' 8080 ','')
                                                string_new_server_name = string_new_server_name.replace(' 8443 ','')
                                                string_new_server_name = string_new_server_name.replace('443 ','')
                                                string_new_server_name = string_new_server_name.replace('80 ','')
                                                string_new_server_name = string_new_server_name.replace('8080 ','')
                                                string_new_server_name = string_new_server_name.replace('8443 ','')

                                                # Remove common cases of spacing and dividers
                                                string_new_server_name = string_new_server_name.replace(' - ','-')
                                                string_new_server_name = string_new_server_name.replace(' -','-')
                                                string_new_server_name = string_new_server_name.replace('- ','-')
                                                # Final catch any remaining spacing
                                                string_new_server_name = string_new_server_name.replace(' ','-')
                                                string_new_server_name = string_new_server_name.removeprefix('-')
                                                string_new_server_name = string_new_server_name.removesuffix('-')

                                                # No need to update if name hasn't changed
                                                if old_server_name != string_new_server_name:
                                                    print("Found - Attempting to Swap Node Server Name")
                                                    print(old_server_name + ' -> ' + string_new_server_name)
                                                    # Update the address to the new value, from lookup of old/new dictionary
                                                    pool_member_server['name'] = string_new_server_name
                                                new_pool_member_servers.append(pool_member_server)

                                        except KeyError:
                                            # Catch if no server Name present
                                            print("Exception on Server Name Swap: " + class_of_application)
                                            pass

                                        # Sanity Check before update
                                        if len(pool_member['servers']) == len(new_pool_member_servers):
                                            # Done parsing 'servers' so update object in the members list
                                            pool_member['servers'] = new_pool_member_servers
                                            # Append to updated members list
                                            new_pool_members.append(pool_member)
                                        else:
                                            print("Failed to update Servers list inside Member list of pool for: " + source['declaration'][dec_key][tenant_key][application_key])
                                            pass

                                    # Sanity Check before update
                                    if len(source['declaration'][dec_key][tenant_key][application_key]['members']) == len(new_pool_members):
                                        source['declaration'][dec_key][tenant_key][application_key]['members'] = new_pool_members
                                    else:
                                        print("Failed to update Node Names in: " + source['declaration'][dec_key][tenant_key][application_key])
                                        pass

                            except TypeError:
                                pass
                            except KeyError:
                                pass
                    except TypeError:
                        pass
                    except KeyError:
                        pass
            except TypeError:
                pass
            except KeyError:
                pass
            except Exception as error:
                print(type(error).__name__)
                print(error)

    # output_filename = str(in_filename + '_updated.json')
    output_filename = str(in_filename)

    with open(output_filename, "w") as outfile: 
        json.dump(source, outfile, indent=2)

# TODO: Remove SA if just enabled

def Simplify_tcp_profiles(in_filename) -> None:
    '''
    Parses F5 AS3 JSON File, looks for tcp profiles that only customize timeout value - simplifies with consistent naming and consolidates in app
    This is destructive of original file, please backup file prior to running.
    '''

    destination = {}

    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        for dec_key in source:
            value_of_key = source[dec_key]
            #print(value_of_key)
            destination[dec_key] = value_of_key
        
    # Close source file to prevent dictionary size change error

    # Reopen source file
    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)


        for dec_key in source['declaration']:
            # print(source['declaration'][i])
            try:
                for tenant_key in source['declaration'][dec_key]:

                    #list_of_tcp_found = []
                    tcp_profile_replacement_dict = {}
                    vs_list = {}

                    try:
                        for application_key in source['declaration'][dec_key][tenant_key]:

                            try:
                                # name_of_application = source['declaration'][dec_key][tenant_key][application_key]
                                class_of_application = source['declaration'][dec_key][tenant_key][application_key]['class']
                                
                                if class_of_application[0:8] == 'Service_':
                                    # Catch most Service classes with profileTCP
                                    try:
                                        active_profileTCP = source['declaration'][dec_key][tenant_key][application_key]['profileTCP']["use"]
                                        vs_list[application_key] = {'vs_name':application_key,'tcp_profile':active_profileTCP}
                                    except KeyError:
                                            # Catch if no server Name present
                                        pass
                                if class_of_application == 'TCP_Profile':
                                    # Catch TCP Profile
                                    #list_of_tcp_found.append(application_key)
                                    # Check if only 1 customization is present
                                    if len(source['declaration'][dec_key][tenant_key][application_key]) == 2:
                                        # Catch if the only customization the TCP profile has is the idleTimeout set
                                        try:
                                            tcp_idle_timeout = source['declaration'][dec_key][tenant_key][application_key]['idleTimeout']
                                            # print(tcp_idle_timeout)
                                            old_tcp_profile_name = application_key
                                            new_tcp_profile_name = 'tcp_timeout_' + str(tcp_idle_timeout)
                                            tcp_profile_replacement_dict[old_tcp_profile_name] = {'tcp_profile':new_tcp_profile_name,'tcp_timeout':tcp_idle_timeout}

                                        except TypeError:
                                            pass
                                        except KeyError:
                                            pass
                            except TypeError:
                                pass
                            except KeyError:
                                pass
                    except TypeError:
                        pass
                    except KeyError:
                        pass

                    try:
                        # Walk through and update TCP Profile references in VS
                        for element in vs_list:
                            application_key = vs_list[element]['vs_name']
                            active_profileTCP = vs_list[element]['tcp_profile']
                            new_tcp_profile_name = tcp_profile_replacement_dict[active_profileTCP]['tcp_profile']
                            # Update VS to use new profile
                            destination['declaration'][dec_key][tenant_key][application_key]['profileTCP']["use"] = new_tcp_profile_name
                       # Walk through and update TCP Profiles in APP
                        for element in tcp_profile_replacement_dict:
                            new_tcp_profile_name = tcp_profile_replacement_dict[element]['tcp_profile']
                            tcp_idle_timeout = tcp_profile_replacement_dict[element]['tcp_timeout']
                            new_tcp_profile_obj = {'idleTimeout':tcp_idle_timeout, "class": "TCP_Profile"}
                            # Remove old profile to app
                            destination['declaration'][dec_key][tenant_key].pop(element)
                            # Add new profile to app
                            destination['declaration'][dec_key][tenant_key][new_tcp_profile_name] = new_tcp_profile_obj

                    except TypeError:
                        pass
                    except KeyError:
                        pass

            except TypeError:
                pass
            except KeyError:
                pass
            except Exception as error:
                print(type(error).__name__)
                print(error)

    # output_filename = str(in_filename + '_updated.json')
    output_filename = str(in_filename)

    with open(output_filename, "w") as outfile: 
        json.dump(destination, outfile, indent=2)

def Mass_f5_flipper_split_apps(in_filename:str, folder_name_json='mass_convert_export_json', folder_name_ns='mass_convert_export_ns') -> None:
    '''
    Parses F5 Flipper mass export JSON File, looks for each APP's AS3 and NS Conf lines and creates a file for each.
    Requires input filename to be passed, optionally can provide destination json and destination ns folder names.
    If no destination folders provided defaults to 'mass_convert_export_json' and 'mass_convert_export_ns' folders.
    '''

    # Reopen source file
    with open(in_filename, 'r') as vars_file:
        source = json.load(vars_file)

        for app_list_item in source['apps']:

            try:
                for dec_key in app_list_item['as3']['declaration']:
                    
                    try:
                        for tenant_key in app_list_item['as3']['declaration'][dec_key]:
                            try:
                                # Path to container AS3 app_list_item['as3']
                                # Path to container NS Lines app_list_item['sourceLines']

                                # Useful paths
                                # name_of_tenant_container = app_list_item['as3']['declaration'][dec_key]
                                # name_of_app_container = app_list_item['as3']['declaration'][dec_key][tenant_key]
                                # class_of_app_container = app_list_item['as3']['declaration'][dec_key][tenant_key]['class']

                                class_of_application = app_list_item['as3']['declaration'][dec_key][tenant_key]['class']
                                if class_of_application == 'Application':

                                    # Prepare Destination File name based on Application Name
                                    destination_as3_name = tenant_key
                                    destination_nsconf_name = tenant_key

                                    destination_as3_dict = app_list_item['as3']
                                    # destination_as3_name = app_list_item['as3']['declaration']['id']

                                    destination_nsconf_list = app_list_item['sourceLines']
                                    # destination_nsconf_name = app_list_item['as3']['declaration']['id']

                                    destination_as3_name = str(folder_name_json) + '/' + str(destination_as3_name) + '.json'
                                    destination_nsconf_name = str(folder_name_ns) + '/' + str(destination_nsconf_name) + '.conf'

                                    with open(destination_as3_name, "w") as outfile: 
                                        json.dump(destination_as3_dict, outfile, indent=2)
                                    
                                    with open(destination_nsconf_name, "w", newline='') as outfile: 
                                        outfile.writelines('\n'.join(str(line) for line in destination_nsconf_list)+'\n')
                            except TypeError:
                                pass
                            except KeyError:
                                pass
                    except TypeError:
                        pass
                    except KeyError:
                        pass

            except TypeError:
                pass
            except KeyError:
                pass
            except Exception as error:
                print(type(error).__name__)
                print(error)

if __name__ == "__main__":
    # Testing with single file run as script rather than imported function
    Add_pool_service_port('example_good_as3.json')
    Update_vip_ip('example_good_as3.json')
    Update_tenant_name('example_good_as3.json')
    Update_schema('example_good_as3.json')
    Count_vips('example_good_as3.json')
    Clean_up_node_names('example_good_as3.json')
    Simplify_tcp_profiles('example_good_as3.json')
