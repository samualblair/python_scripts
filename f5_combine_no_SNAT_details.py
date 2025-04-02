# Created by: Michael Johnson - 11-21-2024
# Leveraging a json file that was previously created, such as the one from f5py module
# Parsing code to filter out information regarding virtual servers
# Specifically create both:
#  1) A Virtual Server summary output file
#  2) (only where relevent) a Virtual Server summary file of VS that do not have SNAT (no_SNAT)

import os
# import pprint

def print_output_values(reading_file:str='virtuals_all_no_snat_outfile.txt') -> None:
    """
    Reviews Output Text files previously created from parsing, outputs to console and saves to file
    """

    with open(reading_file, 'r') as vars_file:
        source = vars_file.read()

    print(source)

    # Outfile string
    outfile_string = "combined_no_snat_outfile.txt"
    # More predictable to use this style - append to file as this will be itterated on
    with open(outfile_string, 'a') as outfile:
        outfile.write(source)

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
                        # Only try to parse file if it is name ends with _no_snat_outfile.txt
                        if file_name[-20:] == "_no_snat_outfile.txt":
                            print_output_values(file_contents)
                    # Catch when file is not parsable UTF 8 or similar
                    except UnicodeDecodeError:
                        print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
    except IndexError:
        print('Issue with file - ' + file_name)
