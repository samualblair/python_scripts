# Merging Steps - via CLI

For merge these steps can be taken to script things out

First unpack sources

```bash
mkdir ucs1a_v15_new_key_unpacked
mkdir ucs2a_v15_new_key_unpacked
mkdir ucs3a_v15_new_key_unpacked
mkdir merged_unpacked
tar -xzvf ucs1a_v15_new_key.ucs -C ucs1a_v15_new_key_unpacked
tar -xzvf ucs2a_v15_new_key.ucs -C ucs2a_v15_new_key_unpacked
tar -xzvf ucs3a_v15_new_key.ucs -C ucs3a_v15_new_key_unpacked
```


Next - Build Merged Folder with all files from all archive - Just Chose a single method

```bash
# Method 1
# Start with base or highest priority to keep with conflicts
tar xzvf ucs1a_v15_new_key.ucs -C ./merged_unpacked
# Overide conflicts with 2nd, ensures missing files are added
cp -R ucs2a_v15_new_key_unpacked/* ./merged_unpacked
# Overide conflicts with 3rd, ensures missing files are added
cp -R ucs3a_v15_new_key_unpacked/* ./merged_unpacked
# Overide conflicts with base (or highest priority to keep with conflicts) again, ensrues any references in base remain predictable
cp -R ucs1a_v15_new_key_unpacked/* ./merged_unpacked

# Alternative Method #2 'Quick' method - should give same results with less steps ... would be worth additonal conflict testing to confirm
# Overide conflicts with 2nd, ensures missing files are added
cp -R ucs2a_v15_new_key_unpacked/* ./merged_unpacked
# Overide conflicts with 3rd, ensures missing files are added
cp -R ucs3a_v15_new_key_unpacked/* ./merged_unpacked
# Overide conflicts with base again, ensrues any references in base remain predictable
cp -R ucs1a_v15_new_key_unpacked/* ./merged_unpacked

# Alternative Method #3 Full 'Rsync' method - should give the same results, but would prioritize 'newest' file not just 'chosen base'
# As long as all sources have same master key this should be fine, but ... would be worth additonal conflict testing to confirm otherwise a little uncomfortable doing this for whole ucs
# Rsync is certainly aceptable for just certs and keys, but this example is for all files
# Start with base
tar xzvf ucs1a_v15_new_key.ucs -C ./merged_unpacked
# Rsync over others. Note rsync exclude string needs to escape the period '.' character
rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-f5a_unpakced/var/tmp/filestore_temp/ ./new-f5a_unpakced/var/tmp/filestore_temp
rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-f503_unpakced/var/tmp/filestore_temp/ ./new-f5a_unpakced/var/tmp/filestore_temp
rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-f501_unpakced/var/tmp/filestore_temp/ ./new-f5a_unpakced/var/tmp/filestore_temp

# Alternative Method 4 Minimal 'Rsync' method - only filestore
# Rsync over files from filestore_temp - should be completely safe if desired - but may require coming back and grabbing other folders later
# Start with base
tar xzvf ucs1a_v15_new_key.ucs -C ./merged_unpacked
# Rsync over known required files from filestore. Note rsync exclude string needs to escape the period '.' character
rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-f503_unpakced/var/tmp/filestore_temp/ ./new-f5a_unpakced/var/tmp/filestore_temp
rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-f501_unpakced/var/tmp/filestore_temp/ ./new-f5a_unpakced/var/tmp/filestore_temp
```

Now, find source files that can be used for merge process, and concatenate (join) using cat to get started.

```bash
find . -name bigip.conf | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"
find . -name bigip_base.conf | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"
# find . -name BigDB.dat | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"

# First file referenced will be first in new file - this should be the base or highest priority to keep with conflicts
cat ./ucs1a_v15_new_key_unpacked/config/bigip.conf ./ucs2a_v15_new_key_unpacked/config/bigip.conf ./ucs3a_v15_new_key_unpacked/config/bigip.conf > ./merged_unpacked/config/bigip.conf
cat ./ucs1a_v15_new_key_unpacked/config/partitions/aci_partition/bigip.conf ./ucs3a_v15_new_key_unpacked/config/partitions/aci_partition/bigip.conf > ./merged_unpacked/config/partitions/aci_partition/bigip.conf

# Will need to repeate this process for each partition as well
# First file referenced will be first in new file - this should be the base or highest priority to keep with conflicts
cat ./ucs1a_v15_new_key_unpacked/config/bigip_base.conf ./ucs2a_v15_new_key_unpacked/config/bigip_base.conf ./ucs3a_v15_new_key_unpacked/config/bigip_base.conf > ./merged_unpacked/config/bigip_base.conf
cat ./ucs1a_v15_new_key_unpacked/config/partitions/aci_partition/bigip_base.conf ./ucs3a_v15_new_key_unpacked/config/partitions/aci_partition/bigip_base.conf > ./merged_unpacked/config/partitions/aci_partition/bigip_base.conf
```

Optionally, this is a good time to copy out into a working folder to edit, start a local git repo and use git to track changes. If you do just remember to copy back before rearchiving. Either way now is the time to finish editing the 'merge' conf files.

```bash
find ./merged_unpacked/ -name bigip.conf | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"
find ./merged_unpacked/ -name bigip_base.conf | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"

# May output something like
./new-f5a_unpakced/config/bigip.conf
./new-f5a_unpakced/config/partitions/aci_partition/bigip.conf
./new-f5a_unpakced/config/bigip_base.conf
./new-f5a_unpakced/config/partitions/aci_partition/bigip_base.conf

# Can copy out to new folder with:
mkdir working_git
cp ./merged_unpacked/config/bigip.conf ./working_git/common_bigip.conf 
cp ./merged_unpacked/config/partitions/aci_partition/bigip.conf ./working_git/aci_partition_bigip.conf 
cp ./merged_unpacked/config/bigip_base.conf ./working_git/common_bigip_base.conf 
cp ./merged_unpacked/config/partitions/aci_partition/bigip_base.conf ./working_git/aci_partition_bigip_base.conf 

# Go into folder, start git repo, drop back, launch Visual Studio Code editor on that folder for easy editing
cd working_git
git init
cd ..
code ./working_git

# After working on can copy updated files back with
cp ./working_git/common_bigip.conf ./merged_unpacked/config/bigip.conf
cp ./working_git/aci_partition_bigip.conf ./merged_unpacked/config/partitions/aci_partition/bigip.conf
cp ./working_git/common_bigip_base.conf ./merged_unpacked/config/bigip_base.conf
cp ./working_git/aci_partition_bigip_base.conf ./merged_unpacked/config/partitions/aci_partition/bigip_base.conf
```

When finished with edits , now it is time to rearchive (create the new UCS file)
```bash
# CMD1: Exclude statement must be before -czvf. Note 'tar' exclude does not need to escape the period '.' character
tar --disable-copyfile --exclude='._*' --exclude='.DS_Store' -czvf ../2025_05_16_f5a.ucs *

# CMD 2: Alternative but equally valid method to create UCS
find "merged_unpacked"/ -type f -o -type l -o -type d | sed s,^"merged_unpacked"/,, | grep -v -E "\._|\.DS_Store" | tar --disable-copyfile -czf "../2025_05_16_f5a.ucs" --no-recursion -C "merged_unpacked"/ -T -
```

Some additional Verification and/or Cleanup Commands - For MacOS systems
```bash
# Handy commands to verify and/or cleanup before creating UCS. Note 'find' does not need to escape the period '.' character
find . -name '._*'
find . -name '._*' -delete
find . -name '.DS_Store'
find . -name '.DS_Store' -delete
# Handy commands to verify UCS anyway, ensure it doesn't have any unwanted files , note 'grep' must escape the period '.' character
tar -tzf name.ucs | grep -E '\._|\.DS_Store'
```

When ready cleanup can be done in GUI or CLI, on CLI must run with eleveated permissions or change file permissions as many files are marked as read-only
```bash
# Cleanup Example - can remove anytime after initial copy merge, and .conf file concatenate (join) are done
sudo su
rm -R ucs1a_v15_new_key_unpacked
rm -R ucs2a_v15_new_key_unpacked
rm -R ucs3a_v15_new_key_unpacked
exit

# Can do similar for unpacked merged folder, once you have a working archive (UCS) file - Don't remove this until it is absolutly not needed
sudo su
rm -R merged_unpacked
exit
```
