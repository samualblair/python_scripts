# Created by: Michael Johnson - 04-27-2025
# Re-archive ucs folders
import os
import subprocess

def archive_ucs(bigip_conf_folder:str,file_extention_length:int=0) -> None:
    """
    Archives the provided folder name and creates a .ucs file in parent directory with original directory name and _new.ucs appended.
    Allows entering number of charachters to be removed form name , for example to remove _unpacked that is 9 charachters should be removed from name.
    """

    if len(bigip_conf_folder) == 0:
        print('No folder name provided')
        return

    if file_extention_length < 0:
        print('New UCS name trim length cannot be a negative number, not triming new ucs name')
        file_extention_length = 0

    if len(bigip_conf_folder) - file_extention_length < 1:
        print('New UCS name trim length is to large, not triming new ucs name')
        file_extention_length = 0

    # New file name should be old path without '_unpacked' or -9 charachters, then add '_new.ucs' to end
    path_of_new_ucs_file = (f'{bigip_conf_folder[0:len(bigip_conf_folder)-file_extention_length]}_new.ucs')

    # Inform User of Creation Start
    print(f'Starting Creating of archive: "{path_of_new_ucs_file}" from "{bigip_conf_folder}"')

    # Change to directory
    # print(os.getcwd())
    #Store Old
    old_working_directory = os.getcwd()
    # print("Was.. "+old_working_directory)
    os.chdir(f"{bigip_conf_folder}")
    # print("Now.. "+os.getcwd())

    # Create Archive. Note 'tar' exclude does not need to escape the period '.' character
    sub_comamnd = f'tar --disable-copyfile --exclude="._*" --exclude=".DS_Store" -czf "../{path_of_new_ucs_file}" *'
    subprocess.run(sub_comamnd, shell=True)

    # Archive Created
    # print(f'Finished archive: {os.getcwd()}/../{bigip_conf_folder}')
    print(f'Finished Creating of archive: "{path_of_new_ucs_file}" from "{bigip_conf_folder}"')

    os.chdir(f"{old_working_directory}")
    # print(os.getcwd())

if __name__ == "__main__":
    # Assign starting directory to recursivly work in
    directory = input('Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )\n')

    # Assuming _unpacked in folder name , this would be 9 charachters that should be removed
    characters_to_trim = int(input('Please enter the number of charachters you want to trim from folder name (HINT: removing "_unpacked" would be 9)\n'))

    archive_ucs(directory,characters_to_trim)

    # # Iterate over files in the directory, Walk directory tree and record for later use
    # recursive_folder_list = []    

    # # Re-Archive in new UCS
    # for folder_name in extracted_folders_list:
    #     archive_ucs(folder_name)
