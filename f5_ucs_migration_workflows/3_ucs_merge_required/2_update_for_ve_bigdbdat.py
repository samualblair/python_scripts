# Created by: Michael Johnson - 04-09-2025
# Parsing code to update BigDB.dat file for UCS migration to VE
import os
import configparser
from stat import S_IRUSR, S_IRGRP, S_IROTH, S_IWUSR


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




if __name__ == "__main__":
    # assign directory
    directory = input('Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )\n')

    # iterate over files in
    # that directory
    # Walk directory tree and record for later use
    recursive_folder_list = []    
    for currentpath, folders, files in os.walk(directory):
        for folder in folders:
            # print(os.path.join(currentpath, file))
            recursive_folder_list.append(os.path.join(currentpath, folder))
    # Also add base folder to list
    recursive_folder_list.append(directory)

    # print(sys.argv[1])
    try:
        for folder_name in recursive_folder_list:
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
