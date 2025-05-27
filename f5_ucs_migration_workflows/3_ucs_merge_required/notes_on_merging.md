

# Create Priorities of merging
Creating a list/priority for merging helps to track what you are doing, and where to override when conflicts.

* Top priority when merging
    * OLD-F5A / OLD-F5B

* If needed when mergeing
    * OLD-F503 / OLD-F504

* If needed when mergeing
    * OLD-F501 / OLD-F502

And the resulting file:
* New Names (combined)
    * NEW-F5A / NEW-F5B


# Tricks when working with archives

## When ready to load the UCS on a new platform

* Use no-license , when the new system already is licensed and you are not tring to bring in a license file with the backup
* Use the platform-migrate option, to allow proper loading on new hardware or VM
* Use the keep-current-management-ip, to allow loading when a new management IP is already set and you don't want to lose it

Example:
```
tmsh load sys ucs NEW-F5A.ucs no-license platform-migrate keep-current-management-ip
```

## Linux

* Not to much to worry about, will behave similar to F5 (which is a form of Red Hat Linux)

## MacOS

* When using tar , cp, scp, rsync and others (finder) macos will create unwanted files
  * .DStore , this can cause problems in some cases if in the wrong place on the F5
  * ._filname , this is likely to cause problems as it may show up all over the place
    * For example: If you have 3 files folder/file1 file2 folder3/subfolder3/file3
    * MacOS will make the as well: folder/._file1 ._file2 folder3/subfolder3/._file3
    * This is very likely to cause problems when extracting the UCS
* There are various ways to try and avoid creating, but to remove use this:
  * Find only: 
  * Find and remove: 
* Avoid when using rsync: --exclude='\._*' --exclude='\.DS_Store'
  * Example: rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-hostname/source/ ./new-merged/destination/
* Avoid when using tar: --disable-copyfile
  * Example: tar --disable-copyfile -czvf ../mergednew.ucs *

# A More complete example:

Start with unpacking each to-be-merged ucs.

```bash
mkdir old-f5a_unpakced
mkdir old-f503_unpakced
mkdir old-f501_unpakced
mkdir new-f5a_unpakced
tar -xzvf old-f5a_unpakced -C old-f5a_unpakced
tar -xzvf old.ucs -C old-f503_unpakced
tar -xzvf old.ucs -C old-f501_unpakced

# Extract priority base
tar -xzvf old-f5a_unpakced -C new-f5a_unpakced

# Rsync over files from filestore_temp. Note rsync exclude string needs to escape the period '.' character
rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-f5a_unpakced/var/tmp/filestore_temp/ ./new-f5a_unpakced/var/tmp/filestore_temp
rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-f503_unpakced/var/tmp/filestore_temp/ ./new-f5a_unpakced/var/tmp/filestore_temp
rsync -avh --progress --exclude='\._*' --exclude='\.DS_Store' ./old-f501_unpakced/var/tmp/filestore_temp/ ./new-f5a_unpakced/var/tmp/filestore_temp
```

Now, find source files that can be used for merge process, and concatenate (join) using cat to get started.

```bash
find . -name bigip.conf | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"
find . -name bigip_base.conf | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"
# find . -name BigDB.dat | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"

# First file referenced will be first in new file - this should be the base or highest priority to keep with conflicts
cat ./old-f5a_unpakced/config/bigip.conf ./old-f503_unpakced/config/bigip.conf ./old-f501_unpakced/config/bigip.conf > ./new-f5a_unpakced/config/bigip.conf
cat ./old-f5a_unpakced/config/partitions/aci_partition/bigip.conf ./old-f503_unpakced/config/partitions/aci_partition/bigip.conf > ./new-f5a_unpakced/config/partitions/aci_partition/bigip.conf

# Will need to repeate this process for each partition as well
# First file referenced will be first in new file - this should be the base or highest priority to keep with conflicts
cat ./uold-f5a_unpakced/config/bigip_base.conf ./old-f503_unpakced/config/bigip_base.conf ./old-f501_unpakced/config/bigip_base.conf > ./new-f5a_unpakced/config/bigip_base.conf
cat ./old-f5a_unpakced/config/partitions/aci_partition/bigip_base.conf ./old-f503_unpakced/config/partitions/aci_partition/bigip_base.conf > ./new-f5a_unpakced/config/partitions/aci_partition/bigip_base.conf
```

Optionally, this is a good time to copy out into a working folder to edit, start a local git repo and use git to track changes. If you do just remember to copy back before rearchiving. Either way now is the time to finish editing the 'merge' conf files.

```bash
find ./new-f5a_unpakced/ -name bigip.conf | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"
find ./new-f5a_unpakced/ -name bigip_base.conf | grep -v -E "\.diffVersions|\.bak|openvswitch|conf\.sysinit|conf\.default|defaults/|/bigpipe/"

# May output something like
./new-f5a_unpakced/config/bigip.conf
./new-f5a_unpakced/config/partitions/aci_partition/bigip.conf
./new-f5a_unpakced/config/bigip_base.conf
./new-f5a_unpakced/config/partitions/aci_partition/bigip_base.conf

# Can copy out to new folder with:
mkdir working_git
cp ./new-f5a_unpakced/config/bigip.conf ./working_git/common_bigip.conf 
cp ./new-f5a_unpakced/config/partitions/aci_partition/bigip.conf ./working_git/aci_partition_bigip.conf 
cp ./new-f5a_unpakced/config/bigip_base.conf ./working_git/common_bigip_base.conf 
cp ./new-f5a_unpakced/config/partitions/aci_partition/bigip_base.conf ./working_git/aci_partition_bigip_base.conf 

# Go into folder, start git repo, drop back, launch Visual Studio Code editor on that folder for easy editing
cd working_git
git init
cd ..
code ./working_git

# After working on can copy updated files back with
cp ./working_git/common_bigip.conf ./new-f5a_unpakced/config/bigip.conf
cp ./working_git/aci_partition_bigip.conf ./new-f5a_unpakced/config/partitions/aci_partition/bigip.conf
cp ./working_git/common_bigip_base.conf ./new-f5a_unpakced/config/bigip_base.conf
cp ./working_git/aci_partition_bigip_base.conf ./new-f5a_unpakced/config/partitions/aci_partition/bigip_base.conf
```

When finished with edits , now it is time to rearchive (create the new UCS file)
```bash
# Just to make sure check, and if needed remove unwanted "._" and ".DS_Store" MacOS files. Note 'find' does not need to escape the period '.' character
find . -name '._*'
find . -name '._*' -delete
find . -name '.DS_Store'
find . -name '.DS_Store' -delete

# Modify bigip.conf, bigip_base, Bigdb.dat, etc then when ready re-archive
cd new-f5a_unpakced
# CMD1: Exclude statement must be before -czvf. Note 'tar' exclude does not need to escape the period '.' character
tar --disable-copyfile --exclude='._*' --exclude='.DS_Store' -czvf ../2025_05_16_f5a.ucs *

# CMD 2: Alternative but equally valid method to create UCS
find "merged_unpacked"/ -type f -o -type l -o -type d | sed s,^"merged_unpacked"/,, | grep -v -E "\._|\.DS_Store" | tar --disable-copyfile -czf "../new-f5a.ucs" --no-recursion -C "merged_unpacked"/ -T -

# And copy to new F5
scp ../new-f5a.ucs root@10.10.50.50://var/local/ucs/new-f5a.ucs
```


# Tricks to help parse

## When building ping tests, may be helpful to parse all known IPs:
```bash
tmsh list net self | grep address
tmsh list ltm virtual-address | grep address | grep -v virtual-address
```

## Parsing for key objects
- In 'bigip.conf'
  - Virtual Servers
  - Pools
  - Nodes
  - Monitors
  - Profiles
  - Virtual Addresses 
  - iRules
  - Normal Routes (Network routes)
- In 'bigip_base.conf'
  - Self IPs
  - Route Domains
  - Vlans
  - Management Routes

```bash
# Items present in 'bigip.conf'
grep "ltm virtual-address " bigip.conf
grep "ltm virtual " bigip.conf
grep "ltm pool " bigip.conf
grep "ltm node " bigip.conf
grep "ltm monitor " bigip.conf
grep "ltm rule " bigip.conf
grep "net route " bigip.conf

# Items present in 'bigip_base.conf'
grep "net self " bigip_base.conf
grep "net route-domain " bigip_base.conf
grep "net vlan " bigip_base.conf
grep "sys management-route " bigip_base.conf
```

## Config sections that may be only relevent if keeping ASM
```
# bigip_base
provision asm

# bigip.conf
asm device-sync
asm policy
asm predefined-policy
```

Alternativly: Steps to remove ASM once loaded if that is the route you want to go
[f5-article-K35226430](https://my.f5.com/manage/s/article/K35226430)

## Sometimes APM needs additional folders besides certs
- /var/sam
- /var/tmp/filstore/


# Temp IPs and Testing

May consider assigning Temporary IPs and performing ping testing scripts

## Examples Temp IPs for an HA pair of devices:

**example1.domain.local**

```bash
#example1.domain.local
create net self Self_IP_Mirror_VLAN_3001 address 192.168.252.3/24 allow-service default traffic-group traffic-group-local-only vlan VLAN_Mirror
create net self Self_IP_Peer_VLAN_3002 address 192.168.253.3/24 allow-service default traffic-group traffic-group-local-only vlan VLAN_Peer
create net self Self_IP_VLAN_1000 address 10.10.0.7/24 allow-service none traffic-group traffic-group-local-only vlan VLAN_1000
create net self Self_IP_VLAN_2000 address 11.11.0.7/24 allow-service none traffic-group traffic-group-local-only vlan VLAN_2000
```

**example2.domain.local**
```bash
# example2.domain.local
create net self Self_IP_Mirror_VLAN_3001 address 192.168.252.4/24 allow-service default traffic-group traffic-group-local-only vlan VLAN_Mirror
create net self Self_IP_Peer_VLAN_3002 address 192.168.253.4/24 allow-service default traffic-group traffic-group-local-only vlan VLAN_Peer
create net self Self_IP_VLAN_1000 address 10.10.0.8/24 allow-service none traffic-group traffic-group-local-only vlan VLAN_1000
create net self Self_IP_VLAN_2000 address 11.11.0.8/24 allow-service none traffic-group traffic-group-local-only vlan VLAN_2000
```

**example1.domain.local & example2.domain.local**
```bash
# example1.domain.local , example2.domain.local , FLOATING
create net self Floating_VLAN_1000_1 address 10.10.0.11/24 allow-service none traffic-group traffic-group-1 vlan VLAN_1000
create net self Floating_VLAN_1000_2 address 10.10.0.12/24 allow-service none traffic-group traffic-group-1 vlan VLAN_1000
create net self Floating_VLAN_1000_3 address 10.10.0.13/24 allow-service none traffic-group traffic-group-1 vlan VLAN_1000
create net self Floating_VLAN_2000_1 address 11.11.0.11/24 allow-service none traffic-group traffic-group-1 vlan VLAN_2000
create net self Floating_VLAN_2000_2 address 11.11.0.12/24 allow-service none traffic-group traffic-group-1 vlan VLAN_2000

# Create Net (TMM) Route
create net route Default-GW { gw 10.10.0.1 network 0.0.0.0/0 }

# Create Mgmt (OOB) Route
create sys management-route NTP-1 { gateway 10.1.1.10 network 10.5.5.5/32 }
create sys management-route NTP-2 { gateway 10.1.1.10 network 10.5.5.6/32 }
create sys management-route NTP-3 { gateway 10.1.1.10 network 10.7.7.7/32 }
create sys management-route ISE-1 { gateway 10.1.1.10 network 10.5.5.2/32 }
create sys management-route ISE-2 { gateway 10.1.1.10 network 10.7.7.2/32 }
```

## Examples Testing Script

```bash
# Testing Script - Copy into file and run locally on old/new for easy repeatability
# Test new temp IP's first to ensure no accidental assignments/conflicts exist in network
# Test new temp IP's from Old F5s
# Also new old to old, to ensure no prior issue exists
# Then after configured test all interactions old/new
# MANDATORY: Run on the F5's themselves (old and new)
# OPTIONAL: Run on remote system as well

#! /bin/bash
echo example1.domain.local SELF-IP

#Test HA
ping -c 2 -i .2 192.168.252.3 | grep -e statistics -e received
ping -c 2 -i .2 192.168.253.3 | grep -e statistics -e received

#Test Data (VIPs and Nodes)
ping -c 2 -i .2 10.10.0.7 | grep -e statistics -e received
ping -c 2 -i .2 11.11.0.7 | grep -e statistics -e received

echo example2.domain.local SELF-IP

#Test HA
ping -c 2 -i .2 192.168.252.4 | grep -e statistics -e received
ping -c 2 -i .2 192.168.253.4 | grep -e statistics -e received

#Test Data (VIPs and Nodes)
ping -c 2 -i .2 10.10.0.8 | grep -e statistics -e received
ping -c 2 -i .2 11.11.0.8 | grep -e statistics -e received

echo FLOATING

#Test Data (VIPs and Nodes)
ping -c 2 -i .2 10.10.0.11| grep -e statistics -e received
ping -c 2 -i .2 10.10.0.12| grep -e statistics -e received
ping -c 2 -i .2 10.10.0.13| grep -e statistics -e received
ping -c 2 -i .2 11.11.0.11| grep -e statistics -e received
ping -c 2 -i .2 11.11.0.12| grep -e statistics -e received
```


