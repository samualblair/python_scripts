# F5 UCS Migration Workflows - 2 - Extract archive and perform some changes (no expectation of merging)

This workflow supports taking source UCS files, extracting, modifying where possible, and leaving extracted for further changes.
Specificially this is for minimal changes that are known to need to be made are done, that can all be predicted.
Currently that means only changes needed to alllow a physical UCS to load into a VE (changes to Bigdb.dat file).

This then requires manual work to peform any other changes desired, and a manual rearchive when done.

FUTURE TODO: Add script 2 to re-archive for user as alternative to manually using tar with each unpacked folder

## Modify UCS to migrate physical to VE with Manual Changes needed - Required Process:

Export .ucs files from legacy F5s (multiple sets of config might exist).
  - Upload it to a shared location, or directly to the workstation that will be performing workflow.
  - Example: Place .ucs files under \<file-share-root>/legacy_ucs_configs/\<site>/original
  - Preferably Name the file with hostname, date, version
    
    EXAMPLE:
    ```
    old_hostnameA-01_04012025_v15.ucs
    old_hostnameB-02_04012025_v15.ucs
    ```

Download .ucs file to local folder (best to not work with extracting/re-archiving on remote location)
  - Example: Place .ucs files under \<local-folder-root>/legacy_ucs_configs/\<site>/original

Execute Script 1 against original .ucs file
  - Navigate to script file location (or call out script via full path)
  - Run script 1 (python3 1_extract_modify_update_for_ve_bigdbdat.py)
  - Provide script path for .ucs files
  - Script will complete and will provide extracted copies of all ucs contents for each source device
  - Script will also go through and will modify 'License.MaxCores' value to 8 for each Bigip.dat files
  - Each device will have its own folder (\<ucsname>_unpacked)

Optional (for less confusion) Move extracted folder for each device from 'original' folder into 'unpacked' folder 
  - Example: Place folders with extracted files under \<local-folder-root>/legacy_ucs_configs/\<site>/unpacked

Begin Modification Process (manual text edits)
  - Navigate into each unpacked folder (or location if you did not move it)
  - Update key files: bigip.conf , bigip_base.conf, for Common and any partition
  - *Specifically looking for hostname, mirror cm, vlan, interface, net self (self ip), etc.*

Finish Modification Process    
  - Run 'tar czvf' to create new updated .ucs
    - Ensure when using tar to create without any folder structure
    - One option is move into the unpacked folder and run tar with *:
      ```bash
      local-folder-root/legacy_ucs_configs/<site>/unpacked >
      cd ucsname_unpacked
      local-folder-root/legacy_ucs_configs/<site>/unpacked/ucsname_unpacked >
      tar czf ../new_ucs.tar.gz *
      ```
    - Another option is use something like find to build tar
      ```bash
      find "ucsname_unpacked"/ -type f -o -type l -o -type d | sed s,^"ucsname_unpacked"/,, | tar -czf "new_ucs.tar.gz" --no-recursion -C "ucsname_unpacked"/ -T -
      cd ucsname_unpacked
      tar czf ../newtar.tar.gz *
      ```
  - FUTURE TODO: Add script 2 to re-archive for user as alternative to manually using tar with each unpacked folder

Cleanup: Remove the 'unpacked' folder
  - Not needed - can be safely delted

Optional (for less confusion) Move new .ucs to 'updated' folder.
  - Example: Place .ucs files under \<local-folder-root>/legacy_ucs_configs/\<site>/updated

Optional (for working in a group) Upload new .ucs files to remote folder
  - Example: Place .ucs files under \<file-share-root>/legacy_ucs_configs/\<site>/original

Load on new device (or lab for testing)
  - Ensure new device has a required license level
  - Ensure new device has correct master key
  - Copy / import the new .ucs file to BigIP and laod.


## Script Overviews

## Usage Example for Script 1:
```bash
# run script , and call current folder
python3.13 "1_extract_modify_update_for_ve_bigdbdat.py"
Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )
./
# No Status is shown as extractions are happening
# Script will print on screen status as it updates files or skips over them (for any BigDB.dat file it finds)
Updating [License.MaxCores] with value=8 in the file ./ucs_test/f5_1_backup_unpacked/config/BigDB.dat
Updating [License.MaxCores] with value=8 in the file ./ucs_test/f5_1_backup_unpacked/config/.diffVersions/config/BigDB.dat/BigDB.dat
Updating [License.MaxCores] with value=8 in the file ./ucs_test/f5_2_backup_unpacked/config/BigDB.dat
Updating [License.MaxCores] with value=8 in the file ./ucs_test/f5_2_backup_unpacked/config/.diffVersions/config/BigDB.dat/BigDB.dat
❯

# the 'extracted folder' (with already modified BigDB.dat files) is availble to work in

```
