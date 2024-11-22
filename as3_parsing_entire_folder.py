# Michael W. Johnson - 7-26-2024
# Paring code to parse existing Files in a folder, and call AS3 parsing JSON function on each of those files.

# import required module
import os
import as3_parsing_function as as3_parsing_function

# assign directory
# directory = 'VPXRP01'
directory = input('Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )\n')

# iterate over files in
# that directory
total_vs_counted = 0
try:
    for file_name in os.listdir(directory):
        file_contents = os.path.join(directory, file_name)
        # checking if it is a file
        if os.path.isfile(file_contents):
            as3_parsing_function.Add_pool_service_port(file_contents)
            as3_parsing_function.Update_vip_ip(file_contents)
            as3_parsing_function.Update_tenant_name(file_contents)
            as3_parsing_function.Update_schema(file_contents)
            total_vs_counted += as3_parsing_function.Count_vips(file_contents)

except:
    print('Issue with file - ' + file_name)

print(f'The total number of VS for folder are: {total_vs_counted}')
