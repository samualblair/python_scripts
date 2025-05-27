# Created by: Michael Johnson - 04-27-2025
# Code to remove all MacOS ._ and DS_Store files

import subprocess

# subprocess.run(["ls", "-l"]) 

def clean_macos_dot_files(base_foldername:str='host_ucs_v15_updated') -> None:
    """
    Find all the MacOS generated dotfiles "._" and ".DS_Store" files and remove them
    """

    config_files_sting = ""
    # Run shell commands to get test in byte form , Note 'find' does not need to escape the period '.' character
    config_files_sting_byte = subprocess.Popen(f'find "{base_foldername}" -name "._*"', shell=True, stdout=subprocess.PIPE).stdout.read()
    # Must convert byte recorded output into string output to use in normal string manner
    config_files_sting = config_files_sting_byte.decode('UTF-8')
    # Only run delete if files are found
    if config_files_sting != "":
        print("Found and will remove these ._ files: \n" + config_files_sting)
        sub_comamnd = f'find "{base_foldername}" -name "._*" -delete'
        subprocess.run(sub_comamnd, shell=True)
    else:
        print("No ._ files found")

    config_files_sting = ""
    # Run shell commands to get test in byte form , Note 'find' does not need to escape the period '.' character
    config_files_sting_byte = subprocess.Popen(f'find "{base_foldername}" -name ".DS_Store"', shell=True, stdout=subprocess.PIPE).stdout.read()
    # Must convert byte recorded output into string output to use in normal string manner
    config_files_sting = config_files_sting_byte.decode('UTF-8')
    # Only run delete if files are found
    if config_files_sting != "":
        print("Found and will remove these .DS_Store files: \n" + config_files_sting)
        sub_comamnd = f'find "{base_foldername}" -name ".DS_Store" -delete'
        subprocess.run(sub_comamnd, shell=True)
    else:
        print("No .DS_Store files found")

if __name__ == "__main__":
    # assign directory
    directory = input('Please enter folder name to remove from within recursivly (HINT: may navigate back a folder with ../FOLDERNAME )\n')

    # Remove all dot files recursivly found under directory
    clean_macos_dot_files(directory)
