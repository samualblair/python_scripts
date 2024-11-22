# Created by: Michael Johnson - 11-21-2024
# Leveraging a json file that was previously created, such as the one from f5py module
# Parsing code to filter out information regarding virtual servers
# Specifically create both:
#  1) A Virtual Server summary output file
#  2) (only where relevent) a Virtual Server summary file of VS that do not have SNAT (no_SNAT)

import os
import json
# import pprint

def parse_json_values(bigip_conf_filename:str='virtuals_all.json') -> None:
    """
    Reviews JSON files previously created from F5 python json converter, outputs custom data

    WARNIGN: Only works with supported features (don't expect every config line to be present).

    """

    with open(bigip_conf_filename, 'r') as vars_file:
        source = json.load(vars_file)


    # Wanted virtual server name and IP of vs

    new_dict = {}

    for x in source['virtual_servers']:
        new_dict[x['name']] = {}
        new_dict[x['name']]['name'] = x['name']
        new_dict[x['name']]['destination'] = x['destination']
        try:
            #new_dict[x['name']]['vlans'] = x['vlans'][0]
            if type(x['vlans']) == list:
                new_dict[x['name']]['vlans'] = x['vlans']
                # print(new_dict[x['name']]['vlans'])
                # print('a list')
            else:
                new_dict[x['name']]['vlans'] = x['vlans'][0]
                # print('only one')
        except:
            new_dict[x['name']]['vlans'] = "ANY"
            # print('any')
       
        try:
            new_dict[x['name']]['snatpool'] = x['source-address-translation']['pool']
        except:
            try:
                new_dict[x['name']]['snatpool'] = x['source-address-translation']['type']
            except:
                new_dict[x['name']]['snatpool'] = "NO-SNAT"

    string_dictionary = {}
    string_dictionary['ANY'] = ""

    # Prepare dictionary keys
    for x in new_dict:
        if type(new_dict[x]['vlans']) == list:
            for entry in new_dict[x]['vlans']:
                string_dictionary[entry] = ""
        else:
            entry = new_dict[x]['vlans']
            string_dictionary[entry] = ""

    # Sort ouput by VLAN
    for x in new_dict:
        #print(new_dict[x]['vlans'])

        # value_vlans = new_dict[x]['vlans']
        if type(new_dict[x]['vlans']) == list:
            # print('is a list')
            for entry in new_dict[x]['vlans']:

                working_string = ""
                working_string = working_string + '===' + '\n'
                working_string = working_string + 'Name       : '+ new_dict[x]['name'] + '\n'
                working_string = working_string + 'VS-IP:PORT : '+ new_dict[x]['destination'] + '\n'
                working_string = working_string + 'SNAT-POOL  : '+ new_dict[x]['snatpool'] + '\n'

                current_string = string_dictionary[entry]
                string_dictionary[entry] = current_string + working_string

        else:
            entry = new_dict[x]['vlans']

            working_string = ""
            working_string = working_string + '===' + '\n'
            working_string = working_string + 'Name       : '+ new_dict[x]['name'] + '\n'
            working_string = working_string + 'VS-IP:PORT : '+ new_dict[x]['destination'] + '\n'
            working_string = working_string + 'SNAT-POOL  : '+ new_dict[x]['snatpool'] + '\n'

            current_string = string_dictionary[entry]
            string_dictionary[entry] = current_string + working_string

    printable_string = ""

    for name_of_vlan in string_dictionary:
        header_string = '===' + '\n' + '=== ' + name_of_vlan + ' SECTION ===' + '\n'
        section_string = string_dictionary[name_of_vlan]
        printable_string = printable_string + header_string + section_string

    printable_string = printable_string + '===' + '\n'

    # Outfile string
    outfile_string = bigip_conf_filename + "_outfile.txt"

    # More predictable to use this style
    with open(outfile_string, 'w') as outfile:
        outfile.write(printable_string)

    # Outfile2 string
    outfile_string_2 = bigip_conf_filename + "_no_snat_outfile.txt"

    nosnat_printable_string = ""
    nosnat_string_dictionary = {}

    # Show on screen no SNAT
    for x in new_dict:
        if new_dict[x]['snatpool'] == "NO-SNAT":
            entry = new_dict[x]['name']

            working_string = ""
            working_string = working_string + '===' + '\n'
            working_string = working_string + 'Name       : '+ new_dict[x]['name'] + '\n'
            working_string = working_string + 'VS-IP:PORT : '+ new_dict[x]['destination'] + '\n'
            working_string = working_string + 'SNAT-POOL  : '+ new_dict[x]['snatpool'] + '\n'
            
            if type(new_dict[x]['vlans']) == list:
                # print('is a list')
                for vlan_entry in new_dict[x]['vlans']:
                    working_string = working_string + 'VLAN  : ' + vlan_entry + '\n'
            else:
                vlan_entry = new_dict[x]['vlans']
                working_string = working_string + 'VLAN  : ' + vlan_entry + '\n'

            try:
                current_string = nosnat_string_dictionary[entry]
                nosnat_string_dictionary[entry] = current_string + working_string
            except:
                nosnat_string_dictionary[entry] = working_string

    nosnat_printable_string = ""

    for name_of_vs in nosnat_string_dictionary:
        header_string = '===' + '\n' + '=== ' + name_of_vs + ' SECTION ===' + '\n'
        section_string = nosnat_string_dictionary[name_of_vs]
        nosnat_printable_string = nosnat_printable_string + header_string + section_string

    nosnat_printable_string = nosnat_printable_string + '===' + '\n'

    # Only print file if there is a nonat present
    if nosnat_printable_string != '===' + '\n':

        # More predictable to use this style
        with open(outfile_string_2, 'w') as outfile:
            outfile.write(nosnat_printable_string)


if __name__ == "__main__":
    # assign directory
    # directory = 'VPXRP01'
    directory = input('Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )\n')

    # iterate over files in
    # that directory

    # print(sys.argv[1])
    try:
        for file_name in os.listdir(directory):
            file_contents = os.path.join(directory, file_name)
            # checking if it is a file
            if os.path.isfile(file_contents):
                try:
                    # Only try to parse file if it is name ends with .json
                    if file_name[-5:] == ".json":
                        parse_json_values(file_contents)
                # Catch when file is not parsable UTF 8 or similar
                except UnicodeDecodeError:
                    print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
    except IndexError:
        print('Issue with file - ' + file_name)