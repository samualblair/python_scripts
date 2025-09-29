# Created by: Michael Johnson - 09-15-2025
# Leveraging f5py module
# Paring code to filter out information regarding virtual servers
# IN-PROGRESS 9-15-2025 Barely implements GTM

# import required module
import os
import json
# import pprint
#from f5py import *
# import f5py - NO LONGER NEEDED
# import sys



def parse_tmsh_to_dictionary(string_data):
    """
    Parses output of a tmsh config and adds to a dictionary
    @param out: Command output
    @return: Dictionary
    """

    _new_dictionary = { }
    # _new_dictionary['alltext'] = string_data

    # _config_string_length = len(string_data)

    n_less2_characters = ""
    n_less1_character = ""
    n_character = ""

    # value_recording = False
    first_line = False

    current_string = ""
    # new_string = ""
    commands_lines = []

    for character in string_data:
        n_less2_characters = n_less1_character
        n_less1_character = n_character
        n_character = character
        if first_line:
            if character == "\n":
                if n_less1_character == "\n":
                    commands_lines.append(current_string)
                    current_string = ""
                    n_less2_characters = ""
                    n_less1_character = ""
                    n_character = ""
                    first_line = False
                    continue
        if character == "#":
            first_line = True
        if character == " ":
            if n_less1_character == " ":
                continue
        if character == "{":
            # value_recording = True
            # print(character)
            pass
        if character == "}":
            # print(character)
            # pass
            if n_less1_character == "\n":
                current_string += " "
        if character == "\n":
            # print("before_new_line"+character+"after_a_new_line")
            if n_less1_character == "}":
                if n_less2_characters == "\n":
                    current_string += " "
                    commands_lines.append(current_string)
                    current_string = ""
                    n_less2_characters = ""
                    n_less1_character = ""
                    n_character = ""
                else:
                    continue
            else:
                continue
        else:
            current_string += character
        
    line_count = 0
    for line in commands_lines:
        line_count += 1
        _new_dictionary[line_count] = line

    return _new_dictionary

def parse_tmsh_one_line_to_dict(dict_data):
    """
    Parses output of a tmsh config lines dictionary and add to new dictionary
    @param out: Command output
    @return: Dictionary
    """

    _new_dictionary = { }
    # _new_dictionary['alltext'] = string_data

    # print(_config_string_length)


    for line in dict_data:

        # _new_dictionary[line] = (dict_data[line])
        current_line_string = dict_data[line]

        current_line_string_length = len(current_line_string)
        # print(current_line_string_length)

        if current_line_string_length < 3 :
            print("Skipping Command Less than 3 charachters: 'current_line_string' ")
            continue

        if current_line_string_length > 2:

            if current_line_string[0:3] == "gtm":
                try:
                    len(_new_dictionary["gtm"])
                except KeyError:
                    _new_dictionary["gtm"] = {}

                if current_line_string[4:14] == "datacenter":
                    _name = ""
                    _value = ""
                    setting_value = False
                    for char in current_line_string[15:]:
                        if char == "{":
                            setting_value = True
                        if not setting_value:
                            _name += char
                        elif setting_value:
                            _value += char
                    _name_len = len(_name)
                    _value_len = len(_value)
                    try:
                        len(_new_dictionary["gtm"])
                    except KeyError:
                        _new_dictionary["gtm"] = {}
                    try:
                        len(_new_dictionary["gtm"]["datacenter"])
                    except KeyError:
                        _new_dictionary["gtm"]["datacenter"] = {}
                    _new_dictionary["gtm"]["datacenter"][_name[1:_name_len-1]] = _value[2:_value_len-2]

                elif current_line_string[4:10] == "server":
                    _name = ""
                    _value = ""
                    setting_value = False
                    for char in current_line_string[11:]:
                        if char == "{":
                            setting_value = True
                        if not setting_value:
                            _name += char
                        elif setting_value:
                            _value += char
                    _name_len = len(_name)
                    _value_len = len(_value)
                    try:
                        len(_new_dictionary["gtm"])
                    except KeyError:
                        _new_dictionary["gtm"] = {}
                    try:
                        len(_new_dictionary["gtm"]["server"])
                    except KeyError:
                        _new_dictionary["gtm"]["server"] = {}
                    _new_dictionary["gtm"]["server"][_name[1:_name_len-1]] = _value[2:_value_len-2]

                elif current_line_string[4:10] == "pool a":
                    _name = ""
                    _value = ""
                    setting_value = False
                    for char in current_line_string[11:]:
                        if char == "{":
                            setting_value = True
                        if not setting_value:
                            _name += char
                        elif setting_value:
                            _value += char
                    _name_len = len(_name)
                    _value_len = len(_value)
                    try:
                        len(_new_dictionary["gtm"])
                    except KeyError:
                        _new_dictionary["gtm"] = {}
                    try:
                        len(_new_dictionary["gtm"]["pool a"])
                    except KeyError:
                        _new_dictionary["gtm"]["pool a"] = {}
                    _new_dictionary["gtm"]["pool a"][_name[1:_name_len-1]] = _value[2:_value_len-2]

                elif current_line_string[4:12] == "wideip a":
                    _name = ""
                    _value = ""
                    setting_value = False
                    for char in current_line_string[13:]:
                        if char == "{":
                            setting_value = True
                        if not setting_value:
                            _name += char
                        elif setting_value:
                            _value += char
                    _name_len = len(_name)
                    _value_len = len(_value)
                    try:
                        len(_new_dictionary["gtm"])
                    except KeyError:
                        _new_dictionary["gtm"] = {}
                    try:
                        len(_new_dictionary["gtm"]["wideip a"])
                    except KeyError:
                        _new_dictionary["gtm"]["wideip a"] = {}
                    _new_dictionary["gtm"]["wideip a"][_name[1:_name_len-1]] = _value[2:_value_len-2]

                elif current_line_string[4:11] == "monitor":
                    try:
                        len(_new_dictionary["gtm"]["monitor"])
                    except KeyError:
                        _new_dictionary["gtm"]["monitor"] = {}

                    if current_line_string[12:17] == "https":
                        _name = ""
                        _value = ""
                        setting_value = False
                        for char in current_line_string[18:]:
                            if char == "{":
                                setting_value = True
                            if not setting_value:
                                _name += char
                            elif setting_value:
                                _value += char
                        _name_len = len(_name)
                        _value_len = len(_value)

                        try:
                            len(_new_dictionary["gtm"]["monitor"]["https"])
                        except KeyError:
                            _new_dictionary["gtm"]["monitor"]["https"] = {}

                        _new_dictionary["gtm"]["monitor"]["https"][_name[1:_name_len-1]] = _value[2:_value_len-2]

                    elif current_line_string[12:16] == "http":
                        _name = ""
                        _value = ""
                        setting_value = False
                        for char in current_line_string[17:]:
                            if char == "{":
                                setting_value = True
                            if not setting_value:
                                _name += char
                            elif setting_value:
                                _value += char
                        _name_len = len(_name)
                        _value_len = len(_value)

                        try:
                            len(_new_dictionary["gtm"]["monitor"]["http"])
                        except KeyError:
                            _new_dictionary["gtm"]["monitor"]["http"] = {}

                        _new_dictionary["gtm"]["monitor"]["http"][_name[1:_name_len-1]] = _value[2:_value_len-2]


                    elif current_line_string[12:16] == "smtp":
                        _name = ""
                        _value = ""
                        setting_value = False
                        for char in current_line_string[17:]:
                            if char == "{":
                                setting_value = True
                            if not setting_value:
                                _name += char
                            elif setting_value:
                                _value += char
                        _name_len = len(_name)
                        _value_len = len(_value)

                        try:
                            len(_new_dictionary["gtm"]["monitor"]["smtp"])
                        except KeyError:
                            _new_dictionary["gtm"]["monitor"]["smtp"] = {}

                        _new_dictionary["gtm"]["monitor"]["smtp"][_name[1:_name_len-1]] = _value[2:_value_len-2]

                    elif current_line_string[12:15] == "sip":
                        _name = ""
                        _value = ""
                        setting_value = False
                        for char in current_line_string[16:]:
                            if char == "{":
                                setting_value = True
                            if not setting_value:
                                _name += char
                            elif setting_value:
                                _value += char
                        _name_len = len(_name)
                        _value_len = len(_value)

                        try:
                            len(_new_dictionary["gtm"]["monitor"]["sip"])
                        except KeyError:
                            _new_dictionary["gtm"]["monitor"]["sip"] = {}

                        _new_dictionary["gtm"]["monitor"]["sip"][_name[1:_name_len-1]] = _value[2:_value_len-2]

    return _new_dictionary





def convert_to_json(bigip_conf_filename:str='bigip.conf') -> None:
    """
    Convert a bigip.conf file into a json output. Input filename (default bigip.conf) , output filename.json (ex. bigip.conf.json)

    Can be used to quickly produce JSON to help work with Virtual Server configurations programically

    WARNIGN: Only works with supported features (don't expect every config line to be present).

    """

    with open(bigip_conf_filename, 'r') as input_file:
        f5_config_format = input_file.read()

    config_lines_dict = parse_tmsh_to_dictionary(f5_config_format)
    config_dict = parse_tmsh_one_line_to_dict(config_lines_dict)

    #virtual_server_0 = ltm_code.virtual_servers[0]
    # print(virtual_server_0)
    #dict_format = virtual_server_0.to_dict()

    # Convert to nice indent format
    json_string = json.dumps(config_dict, indent=4)
    # print(json_string)

    with open(bigip_conf_filename[:-5] + '.json', 'w') as input_file:
        input_file.write(json_string + "\n")


if __name__ == "__main__":
    # assign directory
    # directory = 'VPXRP01'
    directory = input('Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )\n')

    # Walk directory tree and record for later use
    recursive_folder_list = []    
    for currentpath, folders, files in os.walk(directory):
        for folder in folders:
            # print(os.path.join(currentpath, file))
            recursive_folder_list.append(os.path.join(currentpath, folder))

    # print(sys.argv[1])
    try:
        for folder_name in recursive_folder_list:
            for file_name in os.listdir(folder_name):
                file_contents = os.path.join(folder_name, file_name)
                # checking if it is a file
                if os.path.isfile(file_contents):
                    try:
                        # Only try to parse file if it is name ends with .json
                        if file_name[-5:] == ".conf":
                            convert_to_json(file_contents)
                    # Catch when file is not parsable UTF 8 or similar
                    except UnicodeDecodeError:
                        print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
    except IndexError:
        print('Issue with file - ' + file_name)
