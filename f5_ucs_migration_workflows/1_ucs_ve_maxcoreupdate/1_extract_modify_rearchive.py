# Created by: Michael Johnson - 04-21-2025
# Parsing code to extract big-ip ucs, update bigdbdat file, and re-archive
import os
import subprocess
import configparser
from stat import S_IRUSR, S_IRGRP, S_IROTH, S_IWUSR

def extract_bigip_archive(bigip_conf_filename:str='support.qkview',file_extention_length:int=7) -> str:
    """
    Extracts All Files from bigip archive - qkview, ucs, generic tar.gz
    Will return string with folder path of extracted (with original name + _unpacked)
    """
    path_of_new_folder = (f'{bigip_conf_filename[0:len(bigip_conf_filename)-file_extention_length]}_unpacked')

    try:
        os.mkdir(path_of_new_folder)
    except FileExistsError:
        print('Folder already existed')

    sub_comamnd = f'tar -xzf "{bigip_conf_filename}" -C "{path_of_new_folder}"'
    subprocess.run(sub_comamnd, shell=True)
    
    return path_of_new_folder

def update_maxcores(bigdb_filename:str='BigDB.dat',file_extention_length:int=4) -> None:
    """
    Directly updates BigDB.dat file
    """

    # Using config parser to read in values and work with them
    bigdb_config = configparser.ConfigParser()

    # Read in config file (BigDB.dat)
    bigdb_config.read(bigdb_filename)

    # If not present, will raise 'KeyError'
    try:
        # Inform user file already have value set
        print('[License.MaxCores] value= is already set to', bigdb_config['License.MaxCores']['value'],'in the file',bigdb_filename)
        # Nothing left to do so return
        return

    except KeyError:
        # Key needs to be set - inform users it will be set
        print('Updating [License.MaxCores] with value=8 in the file',bigdb_filename)

        bigdb_config['License.MaxCores']['value'] = '8'

        # This makes the file read/write for the owner, Read for Group, Read for Other
        os.chmod(bigdb_filename, S_IWUSR|S_IRUSR|S_IRGRP|S_IROTH)

        # Will Fail if file is marked as read-only
        with open(bigdb_filename, 'w') as bigdb_configfile:
            bigdb_config.write(bigdb_configfile, space_around_delimiters=False)

        temp_file_contents = ""
        # Remove blank lines to allow easier error checking by admin
        with open(bigdb_filename, 'r') as bigdb_configfile:
            temp_file_contents = bigdb_configfile.read().replace('\n\n', '\n')
        with open(bigdb_filename, 'w') as bigdb_configfile:
            bigdb_configfile.write(temp_file_contents)

        # This makes the file read only again (User, Group,)
        os.chmod(bigdb_filename, S_IRUSR|S_IRGRP|S_IROTH)

def archive_ucs(bigip_conf_folder:str='support.qkview',file_extention_length:int=9) -> None:
    """
    Archives previously extracted files and folders from bigip archive (ucs, generic tar.gz) into a new ucs archive based on input folder path
    """

    # New file name should be old path without '_unpacked' or -9 charachters, then add '_new.ucs' to end
    path_of_new_ucs_file = (f'{bigip_conf_folder[0:len(bigip_conf_folder)-file_extention_length]}_new.ucs')

    # Inform User of Creation Start
    print(f'Starting Creating of archive: "{path_of_new_ucs_file}" from "{bigip_conf_folder}"')

    # Create Archive
    sub_comamnd = f'find "{bigip_conf_folder}"/ -type f -o -type l -o -type d | sed s,^"{bigip_conf_folder}"/,, | tar -czf "{path_of_new_ucs_file}" --no-recursion -C "{bigip_conf_folder}"/ -T -'
    subprocess.run(sub_comamnd, shell=True)

    # Address tar relative folder creation, use find and sed to deal with issue
    # Credit to ideas in
    # https://stackoverflow.com/questions/939982/how-do-i-tar-a-directory-of-files-and-folders-without-including-the-directory-it
    # OPTION 1a: Deal with issue using GNU Find only Files (f) Links (l) and subdirectories (d) which should be good
    # find "{bigip_conf_folder} \( -type f -o -type l -o -type d \) -printf "%P\n" | tar -czf {path_of_new_ucs_file} --no-recursion -C "{path_of_new_ucs_file}" -T -
    # OPTION 2: Deal with issue using non-GNU Find and sed , using this method for now for better compatability, only Files (f) Links (l) and subdirectories (d) which should be good
    # find "{bigip_conf_folder}"/ -type f -o -type l -o -type d | sed s,^"{bigip_conf_folder}"/,, | tar -czf "{path_of_new_ucs_file}" --no-recursion -C "{bigip_conf_folder}"/ -T -
    # OPTION 2b: Deal with issue using non-GNU Find and sed , using this method for now for better compatability, any type
    # find "{bigip_conf_folder}"/ | sed s,^"{bigip_conf_folder}"/,, | tar -czf "{path_of_new_ucs_file}" --no-recursion -C "{bigip_conf_folder}"/ -T -

    # Archive Created
    print(f'Finished archive: {path_of_new_ucs_file}')

if __name__ == "__main__":
    # Assign starting directory to recursivly work in
    directory = input('Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )\n')

    # Iterate over files in the directory, Walk directory tree and record for later use
    recursive_folder_list = []    
    for currentpath, folders, files in os.walk(directory):
        for folder in folders:
            # print(os.path.join(currentpath, file))
            recursive_folder_list.append(os.path.join(currentpath, folder))
    # Also add base folder to list
    recursive_folder_list.append(directory)

    # Extract UCS files found
    # Store list of extracted folders for future reference
    extracted_folders_list = []
    try:
        for folder_name in recursive_folder_list:
            for file_name in os.listdir(folder_name):
                file_contents = os.path.join(folder_name, file_name)
                # checking if it is a file
                if os.path.isfile(file_contents):
                    try:
                        # Only try to parse file if it is name ends with .ucs or .tar.gz
                        if file_name[-7:] == ".tar.gz":
                            # Extract archive and store returned extracted folder
                            extracted_folders_list.append(extract_bigip_archive(file_contents))
                        elif file_name[-4:] == ".ucs":
                            # Extract archive and store returned extracted folder
                            extracted_folders_list.append(extract_bigip_archive(file_contents,4))
                    # Catch when file is not parsable UTF 8 or similar
                    except UnicodeDecodeError:
                        print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
    except IndexError:
        print('Issue with file - ' + file_name)

    # # Modify Bigip.dat files - should be known location inside exctracted folder - so direct edit is possible
    # # Concerns about folder pathing on different OSes (LINUX/MACOS/UNIX/POSIX use '/' and WINDOWS uses '\') , only defined for non-windows
    # for extracted_folder in extracted_folders_list:
    #     bigip_dat_filename = extracted_folder + '/config/BigDB.dat'
    #     try:
    #         update_maxcores(bigip_dat_filename)                            
    #     # Catch when file is not parsable UTF 8 or similar
    #     except UnicodeDecodeError:
    #         print('Fail to read file - ' + bigip_dat_filename + ' : Is this a file to be read?')
    #     except IndexError:
    #         print('Issue with file - ' + bigip_dat_filename)

    # Modify Bigip.dat files
    # Using discovery also helps potentially make script more os portable in future to other OSes
    # Iterate over files in the previous directories, Walk directory tree and record for later use
    extracted_recursive_folder_list = []
    for extracted_folder in extracted_folders_list:
        for currentpath, folders, files in os.walk(extracted_folder):
            for folder in folders:
                # print(os.path.join(currentpath, file))
                extracted_recursive_folder_list.append(os.path.join(currentpath, folder))
        # Also add base folder to list
        extracted_recursive_folder_list.append(extracted_folder)
    try:
        for folder_name in extracted_recursive_folder_list:
            for file_name in os.listdir(folder_name):             
                file_contents = os.path.join(folder_name, file_name)
                # checking if it is a file
                if os.path.isfile(file_contents):
                    try:
                        # Only try to parse file if it is name ends with "BigDB.dat"
                        if file_name[-9:] == "BigDB.dat":
                            update_maxcores(file_contents)                            
                    # Catch when file is not parsable UTF 8 or similar
                    except UnicodeDecodeError:
                        print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
    except IndexError:
        print('Issue with file - ' + file_name)

    # Re-Archive in new UCS
    for folder_name in extracted_folders_list:
        archive_ucs(folder_name)
