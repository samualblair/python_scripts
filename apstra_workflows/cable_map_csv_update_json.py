# Michael W. Johnson - 02-20-2026
# Paring code to parse Apstra CSV cable map (easy to modify but not importable) - and use it to update an Apstra JSON cable map file (which can be used for import)

import json
import csv


def Update_cable_map_json_from_csv(in_csv_filename:str, in_json_filename:str) -> None:
    '''
    Parses Apstra CSV and JSON cabling-map files to update JSON based on the CSV.
    It is expected that a CSV has been user modified and this needs to be updated in JSON to be able to import into Apstra.
    The updated JSON is created in a new file named {filename}_updated.json, if this file already exists it will be overwritten.
    '''

    # Create dictionary to hold CSV Data
    csv_interface_id_dic = {}

    with open(in_csv_filename, 'r') as csv_vars_file:
        csv_file = csv.DictReader(csv_vars_file)

        for row in csv_file:
            # Warn if object id is missing - skipping entry updates
            if row['Endpoint 1 Interface ID'] == '#NAME?':
                    print('Warning ID Missing - ' + row['Endpoint 1 Name'] + ' to ' + row['Endpoint 2 Interface Name'] )
            elif row['Endpoint 2 Interface ID'] == '#NAME?':
                    print('Warning ID Missing - ' + row['Endpoint 1 Name'] + ' to ' + row['Endpoint 2 Interface Name'] )
            else:
                # Add each interface ID and updated name to dictionary
                csv_interface_id_dic[row['Endpoint 1 Interface ID']] = row['Endpoint 1 Interface Name']
                csv_interface_id_dic[row['Endpoint 2 Interface ID']] = row['Endpoint 2 Interface Name']

    # print(csv_interface_id_dic)

    with open(in_json_filename, 'r') as json_vars_file:
        json_interface_map = json.load(json_vars_file)

        # Walk through each link
        for link_object in json_interface_map['links']:
            # Walk through and update each side of link (each endpoint object)
            for endpoint_list_object in link_object['endpoints']:

                try:
                    # Set ID
                    id_of_object = endpoint_list_object['interface']['id']
                    # Update object from value in csv
                    endpoint_list_object['interface']['if_name'] = csv_interface_id_dic[id_of_object]
                except KeyError:
                    # Catch when key is missing
                    print("Key not found - " + id_of_object)

    output_filename = str(in_json_filename[:-5] + '_updated.json')
    # output_filename = str(in_json_filename)

    # Check file
    finding_duplicates = {}
    # Walk through each link
    for link_object in json_interface_map['links']:
        # Walk through and update each side of link (each endpoint object)
        for endpoint_list_object in link_object['endpoints']:

            # Set System ID
            id_of_system = endpoint_list_object['system']['id']
            # Set ID
            id_of_object = endpoint_list_object['interface']['id']
            # Set Name
            name_of_object = endpoint_list_object['interface']['if_name']

            # check if system present
            try:
                finding_duplicates[id_of_system]
            except KeyError:
                # Catch when key is missing add
                finding_duplicates[id_of_system] = {}

            try:
                finding_duplicates[id_of_system][name_of_object]
                print('Key already present - System ID:' + id_of_system + ' Link ID: ' + id_of_object + 'Interface Name: ' + name_of_object)
            except KeyError:
                # Catch when key is missing
                finding_duplicates[id_of_system][name_of_object] = endpoint_list_object['interface']['if_name']




    with open(output_filename, 'w') as outfile: 
        json.dump(json_interface_map, outfile, indent=2)



if __name__ == '__main__':
    # Testing with single file run as script rather than imported function
    Update_cable_map_json_from_csv('cabling-map.csv', 'cabling-map.json')
