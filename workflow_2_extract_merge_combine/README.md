# F5 Extract and Parse Workflow 2
[![python-version](https://img.shields.io/badge/python-3.13.1-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Looks in destination folder, and subfolders for compressed files (ucs, qkview, or tar.gz). Also extract any certificates and keys into sub folders.

TODO: Proceed to extract entire first (base) configuration archive.
TODO: Merge in additional certificates from other devices.

TODO: : Assist with some of config merges
MANUAL PROCESS: MERGE Configuration from files
- Create new folder with (base) configs
- Merge in configs (bigip.conf , bigip_base.conf, etc) from additional devices into first
- Place new configs into extracted base

TODO: Re-Combined new merged archive so it is ready for use.

## Usage Example for Script 1:
```bash
# Clone into folder ./
# Ensure you are in this folder
❯ pwd
/Users/exampleuser/workingfolder

❯ ls -1
1_extract_all_bigip_config_and_certs_recursive.py


# this folder has all python scripts
# create sub-folder(s) for ucs, qkview, or tar.gz
❯ mkdir ucs_files
❯ mkdir qkviews
❯ mkdir other_names

❯ ls -1
1_extract_all_bigip_config_and_certs_recursive.py
ucs_files
qkviews
other_names

# Move/copy files into ucs_files
run script , and call current folder

# Move/copy files into ucs_files
# run script , and call current folder
❯ python3 "1_extract_all_bigip_config_and_certs_recursive.py"
Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )
./
❯

# Can now confirm extraction has occured for all sub-folders and files
❯ ls -1 -R
1_extract_all_bigip_config_and_certs_recursive.py
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
var # original storage for Certs/Keys folder structure maintained

./ucs_files/F5a-Backup_UCS_unpacked/config:
BigDB.dat # Extracted Database Configuration File
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
./ucs_files/F5a-Backup_UCS_unpacked/var/tmp/filestore_temp/files_d/Common_d:
certificate_d # Extracted 'certificate folder' if present
certificate_key_d # Extracted 'keys folder' configs if present

./ucs_files/F5a-Backup_UCS_unpacked/var/tmp/filestore_temp/files_d/Common_d/certificate_d:
:Common:ca-bundle.crt_20369_1 # Extracted 'certificate file' if present
:Common:default.crt_20367_1 # Extracted 'certificate file' if present
:Common:www.example.com_2048.crt_16915_1 # Extracted 'certificate file' if present

./ucs_files/F5a-Backup_UCS_unpacked/var/tmp/filestore_temp/files_d/Common_d/certificate_key_d:
:Common:default.key_20371_1 # Extracted 'key file' if present
:Common:default.key_20371_1 # Extracted 'key file' if present
:Common:www.example.com_2048.key_17019_1 # Extracted 'key file' if present

## Etc...
```

## Usage Example for Script 2:
```bash
# run script , and call current folder
❯ python3 "2_update_for_ve_bigdbdat.py"
Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )
./

# Script will print on screen status as it updates files or skips over them (for any BigDB.dat file it finds)
Updating [License.MaxCores] with value=8 in the file ./ucs_files/F5a-Backup_UCS_unpacked/config/BigDB.dat
[License.MaxCores] value= is already set to 8 in the file ./ucs_files/F5a-Backup_UCS_unpacked/config/BigDB.dat
[License.MaxCores] value= is already set to 8 in the file ./ucs_files/F5a-Backup_UCS_unpacked/config/BigDB.dat
❯

```

## Authors
[Michael W Johnson](mailto:michael.johnson2@cdw.com)  ([@MichaelWJohnson-Mongoose](https://github.com/MichaelWJohnson-Mongoose))

## Versioning
[![CalVer](https://img.shields.io/static/v1?label=CalVer&message=YY.0M.0D)](https://calver.org/)

* 2025.04.08 - Added BigDB.dat modify for VE change script
* 2025.04.07 - Folder recursion Fixes
* 2025.04.03 - General release
