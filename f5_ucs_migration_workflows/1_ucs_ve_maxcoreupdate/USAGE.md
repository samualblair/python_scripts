# F5 UCS Migration Workflows - 1 - Specific Updates only Required (aka Physical to VE)

This workflow supports taking multiple source UCS files, extracting, modifying, and reachiving for use on new system.
Specificially this is for minimal changes that need to be made, that can all be predicted.
Currently that means only changes needed to alllow a physical UCS to load into a VE (changes to Bigdb.dat file).

## Modify UCS to migrate physical to VE - Required Process:

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
  - Run script 1 (python3 1_extract_modify_rearchive.py)
  - Provide script path for .ucs files
  - Script will complete and will provide extracted copies of all ucs contents for each source device
  - Script will also go through and will modify 'License.MaxCores' value to 8 for each Bigip.dat files
  - Script will also re-archive each file
  - At this point:
    - Each device will have its own folder (/<ucsname>_unpacked) , this can be safely removed
    - Each device will have its own _updated ucs file , this will be kept

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
# Original ucs files shown
❯ ls -1 -R
1_extract_modify_rearchive.py
ucs_test

./ucs_test:
f5_1_backup.ucs
f5_2_backup.ucs

# run script , and call current folder
python3.13 "1_extract_modify_rearchive.py"
# Script will pause and ask you for folder to parse (recursivly)
Please enter folder name to parse all files within (HINT: may navigate back a folder with ../FOLDERNAME )
./
# No Status is shown as extractions are happening
# Script will print on screen status as it updates files or skips over them (for any BigDB.dat file it finds)
Updating [License.MaxCores] with value=8 in the file ./ucs_test/f5_1_backup_unpacked/config/BigDB.dat
Updating [License.MaxCores] with value=8 in the file ./ucs_test/f5_1_backup_unpacked/config/.diffVersions/config/BigDB.dat/BigDB.dat
Updating [License.MaxCores] with value=8 in the file ./ucs_test/f5_2_backup_unpacked/config/BigDB.dat
Updating [License.MaxCores] with value=8 in the file ./ucs_test/f5_2_backup_unpacked/config/.diffVersions/config/BigDB.dat/BigDB.dat
# Script will print on scresn status as it rearchive
Starting Creating of archive: "./ucs_test/f5_1_backup_new.ucs" from "./ucs_test/f5_1_backup_unpacked"
Finished archive: ./ucs_test/f5_1_backup_new.ucs
Starting Creating of archive: "./ucs_test/f5_2_backup_new.ucs" from "./ucs_test/f5_2_backup_unpacked"
Finished archive: ./ucs_test/f5_2_backup_new.ucs

# Script will pause and offer to transfer newly created ucs files to an F5 (into /var/local/ucs via scp)
Do you want to transfer the files? If so type "yes" and if not then type "no" exactly
yes
Please enter hostname or ip of remote f5 for file transfer 
127.0.0.1
Please enter username of remote f5 for file transfer 
user
You will be asked for the password each time, unless using ssh key authentication in which case no password prompt will be shown
Transfers Starting
Starting Transfer of archive: "./ucs_test/f5_1_backup_new.ucs" with username "user"
(user@127.0.0.1) Password:
f5_1_backup_new.ucs                                                                                                                            100%   14MB  90.7MB/s   00:00
Finshed Transfer of archive: "./ucs_test/f5_1_backup_new.ucs"
Starting Transfer of archive: "./ucs_test/f5_2_backup_new.ucs" with username "user"
(user@127.0.0.1) Password:
f5_2_backup_new.ucs                                                                                                                            100%   10MB 144.9MB/s   00:00
Finshed Transfer of archive: "./ucs_test/f5_2_backup_new.ucs"
Transfers Finished

# Script will then pause and ask you if you would like to cleanup unpacked files
Do you want to Cleanup (delete) the unpacked files? If so type "yes" and if not then type "no" exactly)
yes
Starting Cleanups
Starting Removal of unpaked archive: "./ucs_test/f5_1_backup_unpacked"
Removed: "./ucs_test/f5_1_backup_unpacked"
Starting Removal of unpaked archive: "./ucs_test/f5_2_backup_unpacked"
Removed: "./ucs_test/f5_2_backup_unpacked"
Cleanups Finished
❯

# Newly packed UCS files can be seen , in this example unpacked files were cleaned up.
❯ ls -1 -R
1_extract_modify_rearchive.py
ucs_test

./ucs_test:
f5_1_backup_new.ucs
f5_1_backup.ucs
f5_2_backup_new.ucs
f5_2_backup.ucs
❯

# Also remember, if transfers were done and succesful then files with _new.ucs are also located on the f5
```
