# Created by: Michael Johnson - 04-21-2025
# Code to remove all macos ._ files
# May also just conisder bash/sh with one command: find . -name "\._*" -delete

import subprocess

# subprocess.run(["ls", "-l"]) 

def clean_macos_dot_files(base_foldername:str='host_ucs_v15_updated') -> None:
    """
    Find all the dotfiles and remove them
    """
    print(base_foldername)
    # Run shell commands to get test in byte form
    config_files_sting_byte = subprocess.Popen(f'find "{base_foldername}" | grep -E "\\._|\\.DS_Store"', shell=True, stdout=subprocess.PIPE).stdout.read()
    print(config_files_sting_byte)
    
    # Must convert byte recorded output into string output to use in normal string manner
    config_files_sting = config_files_sting_byte.decode('UTF-8')    
    print(config_files_sting)

    # Parse out each line, but ignore the last charachter as it will just be a single new line
    string_list = config_files_sting[0:len(config_files_sting)-1].split("\n")
    print(string_list)

    for config_tar_file_path in string_list:
        # Run shell commands to get test in byte form
        print (f'Removing: "{config_tar_file_path}"')
        sub_comamnd = f'rm "{config_tar_file_path}"'
        subprocess.run(sub_comamnd, shell=True)


if __name__ == "__main__":
    # assign directory
    directory = input('Please enter folder name to remove from within recursivly (HINT: may navigate back a folder with ../FOLDERNAME )\n')

    # Remove all dot files recursivly found under directory
    clean_macos_dot_files(directory)
