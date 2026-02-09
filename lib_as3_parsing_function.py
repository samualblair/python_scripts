# Michael W. Johnson - 02-09-2026
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


if __name__ == "__main__":
    # Testing with single file run as script rather than imported function
    Add_pool_service_port('example_good_as3.json')
    Update_vip_ip('example_good_as3.json')
    Update_tenant_name('example_good_as3.json')
    Update_schema('example_good_as3.json')
    Count_vips('example_good_as3.json')