# F5 UCS Migration Workflows - 3 - Merge Required

This workflow supports taking multiple source UCS files, extracting, modifying, merging, and reachiving for use on new system.
Some of these steps must be done outside of the scripts, the scripts are here to help accelerate the overall process.

## Merge Required Process:

Export .ucs files from legacy F5s (multiple sets of config will exist).
  - Upload it to a shared location, or directly to the workstation that will be performing workflow.
  - Example: Place .ucs files under <file-share-root>\legacy_ucs_configs\<site>\original
  - Preferably Name the file with hostname, date, version
    
    EXAMPLE:
    ```
    old_hostname1-01_04012025_v15.ucs
    old_hostname1-02_04012025_v15.ucs
    old_hostname2-01_04012025_v15.ucs
    old_hostname2-02_04012025_v15.ucs
    old_hostname3_01-04012025_v15.ucs
    old_hostname3_02-04012025_v15.ucs
    ```

Download .ucs file to local folder (best to not work with extracting/re-archiving on remote location)
  - Example: Place .ucs files under <local-folder-root>\legacy_ucs_configs\<site>\original

Execute Script 1 against original .ucs file
  - Navigate to script file location (or call out script via full path)
  - Run script 1 (python3 1_extract_all_bigip_config_and_certs_recursive.py)
  - Provide script path for .ucs files
  - Script will complete and will provide extracted copies of key .conf files and certificates for each source device
  - Each device will have its own folder_unpacked

Execute Script 2 against same location (recursive lookup)
  - Navigate to script file location
  - Run script  (python3 2_update_for_ve_bigdbdat) (or call out script via full path)
  - Provide script path for .ucs files
  - Script will modify 'License.MaxCores' value to 8

Optional (for less confusion) Move extracted folder for each device from 'original' folder into 'unpacked' folder 
  - Example: Place .ucs files under <local-folder-root>\legacy_ucs_configs\<site>\unpacked

Begin Merging Process
  - Create new '<new-hostname>_combined' folder. Will start empty.
  - Copy first config files and certificates
  - Copy additional certificates (feel free to override conflicts - same name)
  - Merge with second set of config files (manual text edits)

Finish Merging Process    
  - Run 'tar xzvf' to extract a single full source device's .ucs file
  - Reference excel spreadsheet "Notes on UCS Merging Many to 1"
  - Copy merged files into new .ucs extracted folder
  - Run 'tar czvf' to create new merged .ucs

Optional (for less confusion) Move new .ucs to 'updated' folder.
  - Example: Place .ucs files under <local-folder-root>\legacy_ucs_configs\<site>\updated

Optional (for working in a group) Upload new .ucs files to remote folder
  - Example: Place .ucs files under <file-share-root>\legacy_ucs_configs\<site>\original

Load on new device (or lab for testing)
  - Ensure new device has a required license level
  - Ensure new device has correct master key
  - Copy / import the new .ucs file to BigIP and laod.


## Script Overviews

Script 1 Overview: 

Looks in destination folder, and subfolders for compressed files (ucs, qkview, or tar.gz). Also extract any certificates and keys into sub folders. 

Script 2 Overview:

Looks in destination folder, and subfolders for BigDB.dat files. Updates the BigDB.dat file for UCS migration to VE (by adding 'License.MaxCores' value=8).

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
