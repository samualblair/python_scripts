# Created by: Michael Johnson - 11-21-2024
# Leveraging f5py module
# Paring code to filter out information regarding virtual servers

# import required module
import os
import json
# import pprint
#from f5py import *
import f5py
# import sys



def convert_to_json(bigip_conf_filename:str='bigip.conf') -> None:
    """
    Convert a bigip.conf file into a json output. Input filename (default bigip.conf) , output filename.json (ex. bigip.conf.json)

    Can be used to quickly produce JSON to help work with Virtual Server configurations programically

    WARNIGN: Only works with supported features (don't expect every config line to be present).

    """

    with open(bigip_conf_filename, 'r') as input_file:
        f5_config_format = input_file.read()

    ltm_code = f5py.LTM(f5_config_format)
    ltm_dict = ltm_code.to_dict()

    #virtual_server_0 = ltm_code.virtual_servers[0]
    # print(virtual_server_0)
    #dict_format = virtual_server_0.to_dict()

    # Convert to nice indent format
    json_string = json.dumps(ltm_dict, indent=4)
    # print(json_string)

    with open(bigip_conf_filename + '.json', 'w') as input_file:
        input_file.write(json_string + "\n")


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
                    convert_to_json(file_contents)
                # Catch when file is not parsable UTF 8 or similar
                except UnicodeDecodeError:
                    print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
    except IndexError:
        print('Issue with file - ' + file_name)
