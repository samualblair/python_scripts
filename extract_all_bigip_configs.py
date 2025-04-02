# Created by: Michael Johnson - 04-1-2025
# Parsing code to extract big-ip configurations from archives
import os
# import json
# import pprint
import subprocess

# subprocess.run(["ls", "-l"]) 

def extract_bigip_conf(bigip_conf_filename:str='support.qkview',file_extention_length:int=7) -> None:
    """
    Extracts Config Files from qkview
    """
#    subcomamnd = f'tar -tzf {bigip_conf_filename}| grep bigip.conf | grep -v -E ".diffVersions|.bak|openvswitch"'
#    subprocess.run(subcomamnd)

    # file_output = subprocess.run(f'tar -tzf {bigip_conf_filename}| grep bigip.conf | grep -v -E ".diffVersions|.bak|openvswitch"', shell=True)
    # print('this_is_file'+file_output)

    # Run shell commands to get test in byte form
    config_files_sting_byte = subprocess.Popen(f'tar -tzf "{bigip_conf_filename}"| grep -E "bigip.conf|bigip_base.conf" | grep -v -E ".diffVersions|.bak|openvswitch|conf.sysinit|conf.default|defaults/|/bigpipe/"', shell=True, stdout=subprocess.PIPE).stdout.read()

    # Must convert byte recorded output into string output to use in normal string manner
    config_files_sting = config_files_sting_byte.decode('UTF-8')    

    # Parse out each line, but ignore the last charachter as it will just be a single new line
    string_list = config_files_sting[0:len(config_files_sting)-1].split("\n")
    # print(string_list)

    try:
        os.mkdir(f'{bigip_conf_filename[2:len(bigip_conf_filename)-file_extention_length]}_unpacked')
    except FileExistsError:
        print('Folder already existed')

    for config_tar_file_path in string_list:
        sub_comamnd = f'tar -xzf {bigip_conf_filename} -C "{bigip_conf_filename[2:len(bigip_conf_filename)-file_extention_length]}_unpacked" "{config_tar_file_path}"'
        subprocess.run(sub_comamnd, shell=True)

        
        #subprocess.run(f'tar -xzf {bigip_conf_filename} -C "unpacked_{bigip_conf_filename[2:len(bigip_conf_filename)]}" "{config_tar_file_path}"', shell=True)

    # f'tar -xzf "{bigip_conf_filename}" -C "unpacked_{bigip_conf_filename}" "config/partitions/EAS-PROD/bigip.conf"'

    # with open(bigip_conf_filename, 'r') as archive_file:
    #     # subprocess.run(["ls", "-l"]) 
    #     print(archive_file)
    #     # subcomamnd = f'tar -tzf {archive_file.name}| grep bigip.conf | grep -v -E ".diffVersions|.bak|openvswitch"'
    #     # subprocess.run(subcomamnd)




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
                    if file_name[-7:] == ".qkview":
                        extract_bigip_conf(file_contents)
                    elif file_name[-7:] == ".tar.gz":
                        extract_bigip_conf(file_contents)
                    elif file_name[-4:] == ".ucs":
                        extract_bigip_conf(file_contents,4)
                # Catch when file is not parsable UTF 8 or similar
                except UnicodeDecodeError:
                    print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
    except IndexError:
        print('Issue with file - ' + file_name)
