# Citrix Netscaler to F5 Conversion Workflow with F5 Flipper

This workflow is to perform a Citrix Netscaler to F5 Conversion. 

Key components of this workflow include: 
* F5 Flipper
  * Extension for MS VSCode
* Python (aid in cleanup)
* F5 AS3 API


## Step 1
Obtain ns.conf file , or tgz backup of netscaler (holds ns.conf file in it)

* Save in folder 'Citrix_configs'
```
./Citrix_configs/ns.conf
```

*NOTE: Good time to commit if using git repo*

## Step 2
Initial cutting of App Configs (NS.conf style) and AS3 Conversion (Initial from F5 Flipper)

* Using VS Code F5 Flipper Extension
  * Right Click on 'ns.conf' file and select 'Explore ADC/NS.conf/tgz'
* Navigate (May auto navigate) to F5 Flipper View
  * Select first APP in APPs
    * Optional - dump csv
  * Click on 'code' button 'looks like notepad' to grab detailed conf lines
    * Save in file , under folder 'Citrix_nsconf_lines', use same name as APP ( eg. App123.conf )
    * Optional - save output from '{}' which includes JSON of details F5 Flipper determined in other location such as Citrix_F5_Flipper_details (eg App123.flipper.json)
  * Click on APP name directly, and render AS3 JSON Declaration
    * Store under AS3 folder (eg. App123.as3.json )
  * Repeat for every APP

Following Files should exist
```
# Required
./AS3/App123.as3.json

# Very Helpful - Expected for manual cleanup reference
./Citrix_nsconf_lines/App123.conf

# Optional
./ns_vips.csv
./Citrix_F5_Flipper_details/App123.flipper.json
```

In larger conversions feel free to create more division under the AS3 folder, such as ./AS3/DC1-INT , ./AS3/DC1-DMZ , ./AS3/DC2-DMZ

*NOTE: Good time to commit if using git repo*

## Step 3 - Start cleaning up AS3 Files

* First run whole folder through a consistency parser (python)
  * This will not change structure of data, but will help with audit/editing
    * Cleanup 1 - Consistent tabs/spacing. Consistent AS3 API version, and schema file reference (to help editor)
    * Cleanup 2 - Ensure UUID is randomized, not all using the same UUID (helps during log hunting in the future, if ever required)
    * TODO: Additional cleanups can be added to Python Script as needed

*NOTE: Good time to commit if using git repo*

## Step 4 - First pass combining Apps, where it makes obvious sense

* First pass walking through and combining Apps into single tenant
  * Goal is first to go from multiple files (each own tenant/declaration) into 1 file
    * For example APP1_443, APP1_80, APP1_8080, APP1_9443
    * Can easily combine all of these into one declaration 'APP1' without much though
      * TODO: Script this out with Python

## Step 5 - Check for any virtual servers with clear conversion errors

* Looking for conflicts that indicate conversion issue
  * One example: An udp server with name _TCP or TCP profile.
    * That doesn't make sense, and is likely a parsing error
    * To really understand the error, and fix, refer to the 'Citrix_nsconf_lines' files for that APP, and the original 'ns.conf' file
  * As needed while parsing - look for any missing references in the original 'ns.conf' file and add those lines into the 'Citrix_nsconf_lines' file for the APP
* Once issue is found , and understood, manually correct AS3 declaration accordingly

## Step 6 - Continued cleanup, to aid in parsing

* Perform any additional desired consistency cleanup
  * Example: remove unnecessary 'Destination Address' reference of 'Service_Address' , as those additional details are only needed if performing some special action (disabling ICMP, disabling ARP, etc)
  * Example: combine list of IPs in a Pool, if not using special names for nodes, and using the same monitor for entire pool. Only need to separate out pool members into individual objects when using custom node names, or customizing monitors for individual nodes.

## Step 7 - Address any Missing WAF Policies

* F5 Flipper does not convert WAF
  * Parse WAF lines, add to 'Citrix_nsconf_lines' file for the APP
  * Determine how to proceed, generally recommend adding new WAF profile
  * WAF profile can be created based on simple template, and saved in folder 'WAF/APP.f5waf.json'
  * WAF Policy can then be base64 encoded into the AS3 declarations

## Step 8 - Address any missing APM (Access) Policies

* F5 APM does not support building policies in AS3, but you can reference them
* Likely need to create custom APM policies in a LAB or on destination device
* Once APM policies are created, they can be exported and stored (backup) in folder 'Access_Polices/APP.f5apm.tar.gz'
* Add reference to various APM polices into the AS3 Declaration

## Step 9 - Deliver AS3 declarations - preferably to a LAB device first

* Help catch any missing logic statements, any conflicts in devices
* Help catch any Tenants/Apps with overlapping Nodes
* Address any Node conflicts either
  * PREFERRED: Merge related APPs into single declaration tenant
  * ALTERNATIVE: If justified, change nodes to 'shared-nodes: True' to have nodes put in '/Common/Shared/' instead of the APP Tenant/Partition and App folder

## Step 10 - Review all items - Declare and Test

* Review everything one last time
* Declare on devices
* Perform Application / User testing

