# Created by: Michael Johnson - 05-15-2025
# Parsing code to extract big-ip ucs, update bigdbdat file, and re-archive, optional transfer and cleanup
import os
import errno
import subprocess
import configparser
from stat import S_IRUSR, S_IRGRP, S_IROTH, S_IWUSR, S_IXUSR

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

def archive_ucs(bigip_conf_folder:str,file_extention_length:int=9) -> str:
    """
    Archives previously extracted files and folders from bigip archive (ucs, generic tar.gz) into a new ucs archive based on input folder path
    """

    # New file name should be old path without '_unpacked' or -9 charachters, then add '_new.ucs' to end
    path_of_new_ucs_file = (f'{bigip_conf_folder[0:len(bigip_conf_folder)-file_extention_length]}_new.ucs')

    # Inform User of Creation Start
    print(f'Starting Creating of archive: "{path_of_new_ucs_file}" from "{bigip_conf_folder}"')

    # Create Archive
    sub_comamnd = f'find "{bigip_conf_folder}"/ -type f -o -type l -o -type d | sed s,^"{bigip_conf_folder}"/,, | grep -v -E "\\._|.DS_Store" | tar --disable-copyfile -czf "{path_of_new_ucs_file}" --no-recursion -C "{bigip_conf_folder}"/ -T -'
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

    return(path_of_new_ucs_file)

def transfer_ucs(bigip_ucs:str,hostname_for_transfer:str,username_for_transfer:str) -> None:
    """
    Transfers ucs to remote device archive based on input file path
    """

    # New file name should be old path without '_unpacked' or -9 charachters, then add '_new.ucs' to end
    bigip_ucs

    # Inform User of Creation Start
    print(f'Starting Transfer of archive: "{bigip_ucs}" with username "{username_for_transfer}"')

    # Transfer ucs via scp
    sub_comamnd = f'scp "{bigip_ucs}" "{username_for_transfer}@{hostname_for_transfer}://var/local/ucs/"'
    subprocess.run(sub_comamnd, shell=True)

    # Archive Created
    print(f'Finshed Transfer of archive: "{bigip_ucs}"')

def cleanup_folder(bigip_ucs_extracted_folder:str) -> None:
    """
    Removes unpacked ucs folder based on input folder path
    """

    # Inform User of Creation Start
    print(f'Starting Removal of unpaked archive: "{bigip_ucs_extracted_folder}"')

    # Make all files writable , include execute on directory, this will allow clean removal
    def recursive_chmod(path):
        for dirpath, dirnames, filenames in os.walk(path):
            os.chmod(dirpath, S_IWUSR|S_IRUSR|S_IRGRP|S_IROTH|S_IXUSR)
            for filename in filenames:
                if os.path.islink(os.path.join(dirpath, filename)):
                    # print(f'Was a symlink: {filename}')
                    # No need to change symlink permissions
                    pass
                else:
                    os.chmod(os.path.join(dirpath, filename), S_IWUSR|S_IRUSR|S_IRGRP|S_IROTH)
    recursive_chmod(bigip_ucs_extracted_folder)

    # Alternative process to Ensure all files are writeable by user, for removal
    # sub_comamnd = f'chmod -R u+w "{bigip_ucs_extracted_folder}"'
    # subprocess.run(sub_comamnd, shell=True)

    # Cleanup - Remove the files and folder
    def recursiveremoval(path):
        for dirpath, dirnames, filenames in os.walk(path):
            for filename in filenames:
                if os.path.islink(os.path.join(dirpath, filename)):
                    # print(f'Was a symlink: {filename}')
                    os.unlink(os.path.join(dirpath, filename))
                else:
                    if os.path.exists(os.path.join(dirpath, filename)):
                        os.remove(os.path.join(dirpath, filename))
                    else:
                        print(f'Tried to delete file but does not exist - {os.path.join(dirpath, filename)}') 
            for dirname in dirnames:
                try:
                    os.rmdir(os.path.join(dirpath, dirname))
                except OSError as error:
                    if error.errno is errno.ENOTEMPTY:
                        recursiveremoval(os.path.join(dirpath, dirname))
            os.rmdir(dirpath)
    recursiveremoval(bigip_ucs_extracted_folder)

    # Alternative process to Remove the files and folder with rm recursive
    # sub_comamnd = f'rm -R "{bigip_ucs_extracted_folder}"'
    # subprocess.run(sub_comamnd, shell=True)

    # Archive Created
    print(f'Removed: "{bigip_ucs_extracted_folder}"')

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
    new_ucs_list_list = []
    for folder_name in extracted_folders_list:
        new_ucs_list_list.append(archive_ucs(folder_name))
    
    # Transfer UCS to F5
    three_tries = 0
    while three_tries < 4:
        # Ask if user wants to transfer all new UCS files
        ask_if_transfer = input('Do you want to transfer the files? If so type "yes" and if not then type "no" exactly\n')

        if ask_if_transfer == "yes":
            # Assign starting directory to recursivly work in
            remote_f5_host = input('Please enter hostname or ip of remote f5 for file transfer \n')
            # Assign starting directory to recursivly work in
            remote_f5_username = input('Please enter username of remote f5 for file transfer \n')
            print('You will be asked for the password each time, unless using ssh key authentication in which case no password prompt will be shown')
            print('Transfers Starting')
            for new_ucs in new_ucs_list_list:
                transfer_ucs(new_ucs,remote_f5_host,remote_f5_username)
            print('Transfers Finished')
            # Finish looping
            three_tries = 4

        elif ask_if_transfer == "no":
            print("Skipping file transfer")
            # Finish looping
            three_tries = 4
       
        else:
            three_tries += 1
            print(f'Not understood, please enter "yes" or "no" - Attmpt {three_tries}')

    if three_tries > 3 and ask_if_transfer != "no" and ask_if_transfer != "yes":
        print("Sorry to many incorrect responses, proceeding to skip file transfer")

    # Cleanup Extracted folders
    three_tries = 0
    while three_tries < 4:
        # Ask if user wants to cleanup (delete) all unpacked UCS files
        ask_if_cleanup = input('Do you want to Cleanup (delete) the unpacked files? If so type "yes" and if not then type "no" exactly\n')

        if ask_if_cleanup == "yes":
            print('Starting Cleanups')
            # Iterate over files in the previous directories, Walk directory tree and record for later use
            for extracted_folder in extracted_folders_list:
                cleanup_folder(extracted_folder)
            print('Cleanups Finished')
            # Finish looping
            three_tries = 4

        elif ask_if_cleanup == "no":
            print("Skipping Cleanups")
            # Finish looping
            three_tries = 4
       
        else:
            three_tries += 1
            print(f'Not understood, please enter "yes" or "no" - Attmpt {three_tries}')

    if three_tries > 3 and ask_if_cleanup != "no" and ask_if_cleanup != "yes":
        print("Sorry to many incorrect responses, proceeding to skip cleanup of unpacked folders")
