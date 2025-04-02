# F5 Extract and Parse Workflow 1
[![python-version](https://img.shields.io/badge/python-3.13.1-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![f5py](https://img.shields.io/badge/f5py-0.3.0-red)](https://pypi.org/project/f5py)

Python Scripts to provide Template Experience with Outlook Client

Ensure dependancies are installed, or available in local folder.
Currently exctracting all configs expects a sub-folder holding the compressed files (ucs, qkview, or tar.gz).

## Usage Example for Script 1:
```bash
# Clone into folder ./
# Ensure you are in this folder
❯ pwd
/Users/exampleuser/workingfolder

❯ ls -1
1 - extract_all_bigip_configs_recursive.py
2 - f5py_convert_to_json_folder_recursive.py
3 - f5py_no_snat_parsing_folder_recursive.py
4 - f5_combine_no_SNAT_details.py

# this folder has all python scripts
# create sub-folder(s) for ucs, qkview, or tar.gz
❯ mkdir ucs_files
❯ mkdir qkviews
❯ mkdir other_names

❯ ls -1
1 - extract_all_bigip_configs_recursive.py
2 - f5py_convert_to_json_folder_recursive.py
3 - f5py_no_snat_parsing_folder_recursive.py
4 - f5_combine_no_SNAT_details.py
ucs_files
qkviews
other_names

# Move/copy files into ucs_files
run script , and call current folder

# Move/copy files into ucs_files
# run script , and call current folder
❯ python3 "1 - extract_all_bigip_configs_recursive.py"
Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )
./
❯

# Can now confirm extraction has occured for all sub-folders and files
❯ ls -1 -R
1 - extract_all_bigip_configs_recursive.py
2 - f5py_convert_to_json_folder_recursive.py
3 - f5py_no_snat_parsing_folder_recursive.py
4 - f5_combine_no_SNAT_details.py
ucs_files
qkviews
other_names

./ucs_files:
F5a-Backup_UCS.ucs
F5a-Backup_UCS_unpacked # New folder with unpacked configs
F5b-Backup_UCS.ucs
F5b-Backup_UCS_unpacked # New folder with unpacked configs

./ucs_files/F5a-Backup_UCS_unpacked:
config # original config folder structure maintained

./ucs_files/F5a-Backup_UCS_unpacked/config:
bigip.conf # Extracted 'common' configs
bigip_base.conf # Extracted 'common' configs
partitions # original config folder structure maintained including partitions

./ucs_files/F5b-Backup_UCS_unpacked/config/partitions:
Prod-App # original config folder structure maintained including partitions
Prod-DMZ # original config folder structure maintained including partitions
Dev-App # original config folder structure maintained including partitions
Dev-DMZ # original config folder structure maintained including partitions

./ucs_files/F5b-Backup_UCS_unpacked/config/partitions/Prod-App:
bigip.conf # Extracted 'partition' configs if present
bigip_base.conf # Extracted 'partition' configs if present (source often may not always have a bigip_base.conf)


## Etc...
```

## Read to run all other scripts in same manner in order (2,3,4):
```bash
> python3 "2 - f5py_convert_to_json_folder_recursive.py"
Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )
./

# Can now confirm extraction has occured for all sub-folders and files from script 2
❯ ls -1 -R
## ommitted all but single example##
./ucs_files/F5a-Backup_UCS_unpacked/config:
bigip.conf
bigip.json # New file in JSON format (proprietary to f5py module)
bigip_base.conf
bigip_base.json # New file in JSON format (proprietary to f5py module)
partitions
## ommitted ##



> python3 "3 - f5py_no_snat_parsing_folder_recursive.py"
Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )
./

# Can now confirm extraction has occured for all sub-folders and files
❯ ls -1 -R
## ommitted all but single example##
./ucs_files/F5a-Backup_UCS_unpacked/config:
bigip.conf
bigip.json
bigip_base.conf
bigip_base.json
bigip_no_snat_outfile.txt # New file for report
bigip_outfile.txt # New file for report
partitions
## ommitted ##

> python3 "4 - f5_combine_no_SNAT_details.py"
Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )
./
## Ommited output report that is printed on screen from script 4 ##
## Can redirect output to file if desired, currently script 4 does not create any files
```

## Authors
[Michael W Johnson](mailto:michael.johnson2@cdw.com)  ([@MichaelWJohnson-Mongoose](https://github.com/MichaelWJohnson-Mongoose))

## Versioning
[![CalVer](https://img.shields.io/static/v1?label=CalVer&message=YY.0M.0D)](https://calver.org/)

* 2025.04.02 - Compare and Except refactoring, added UCS support
* 2025.01.21 - General release
* Pre-release development
