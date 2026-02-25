# Apstra (HPE / Juniper - Apstra Datacenter SDN Manager)

This workflow is around building a Datacenter Blueprint
1) Build out Templates (several)
2) Create Datacenter Blueprint from the Template
3) Update Cable Map
   1) Export existing Cable Map (both JSON and CSV formats)
   2) CSV format may be easier to update quickly/by-human, but Apstra will not allow csv to be re-imported , JSON may not be as quickly/easily updated
   3) Script available to help with exporting port map in csv format, but upload with json format
4) Import Updated Mappings (must use JSON on import)
5) Upload updated Virtual Networks csv
6) Create Connectivity profiles and assign to connections

## Script Overviews

### Script 'cable_map_csv_update_json' Overview: 

- Can be used as library/imported for function 'Update_cable_map_json_from_csv', takes in csv and in json filenames
- If run as script: Looks in folder for two input files 'cabling-map.csv', 'cabling-map.json'
- Uses the CSV to make any needed interface assignment changes against the json, saves as new json file {filename}_updated.json so original json is not lost
- The Updated JSON can be imported into Apstra
