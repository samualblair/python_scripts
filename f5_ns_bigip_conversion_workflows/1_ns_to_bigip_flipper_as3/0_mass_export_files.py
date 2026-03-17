# Michael W. Johnson - 03-17-2026
# Paring code to parse existing Files in a folder, and split out F5 Flipper AS3 and NS conf files for each app.

# import required modules
import os
import lib_as3_parsing_function as lib_as3_parsing_function

# assign directory
# directory = 'mass_convert_source'
directory = input('Please enter folder name to parse all source F5 Flipper files within (Example: ./mass_convert_source )\n')

# iterate over files in
# that directory
total_vs_counted = 0
try:
    for file_name in os.listdir(directory):
        file_contents = os.path.join(directory, file_name)
        # checking if it is a file
        if os.path.isfile(file_contents):  


            # Set the folders to use with mass export
            folder_name_json = 'mass_convert_export_json'
            folder_name_ns = 'mass_convert_export_ns'
            # Ensure Folders expected for 'Mass convert' are present
            try:
                os.mkdir(folder_name_json)
            except FileExistsError:
                pass
            try:
                os.mkdir(folder_name_ns)
            except FileExistsError:
                pass
            
            lib_as3_parsing_function.Mass_f5_flipper_split_apps(file_contents, folder_name_json, folder_name_ns)

except UnicodeDecodeError:
    print('Fail to read file - ' + file_name + ' : Is this a file to be read?')
