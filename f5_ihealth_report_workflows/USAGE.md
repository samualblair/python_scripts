# F5 BIG-IP qKview based iHealth Submit and Report Building

This workflow will have a few steps
1) Creation of Qkview Files (Support Files) - ***no scripts yet***
2) Obtaining of qKview Files - ***no scripts yet***
3) iHealth Submission
4) iHealth Diagnostics Report Download
5) Building of One or More Detailed Reports - ***no scripts yet***

## Script Overviews

## Usage Example for Script 1 - 1_ihealth_submit_and_report : 

### Script 1 Overview - 1_ihealth_submit_and_report : 
Covers Steps 3 & 4 in the workflow.

Users will need iHealth API credentials to upload.
A User can be created at iHealth page [ihealth2](https://account.f5.com/ihealth2) or [ihealth](https://account.f5.com/ihealth).
Navigating to the settings page, and generating a Client ID and Client Secret by clicking the relevant button.

When running the script the user will be prompted to Assign base directory - For parsing QkView Files and storing reports. The script will find all *.QKview files in that folder and upload each of them. They will also be requested to provide a path for the CA (Certificate Authority / CA Bundle used to validate HTTPS connection is secure) - NOTE: Currently the CA check is not enabled so this value is ignored. 

User is provided the following prompts:
   - Please enter your selection - Submit QKview to iHealth or Obtain report ( all , 1_submit , 2_report )
   - Please enter folder name to parse QKview files recursively and/or Store Reports in (HINT: may navigate back a folder with ../FOLDERNAME )
   - Please enter iHealth API Username - This should be API Specific not normal Web Username
   - Please enter iHealth API Password - This should be API Specific not normal Web Password
   - Please enter CA location for iHealth

Regarding selection:
- If user has chosen to all or 1_submit then files will be uploaded, and report_id's will be saved in a list (qkview_id_list.json) for future use.
- If user has chosen to all or 2_report then the list of QKview ID's will be used to obtain diagnostic details.
- If all was chosen, there is an arbitrary 30min wait timer after upload of all files before beginning report gathering (to give iHealth time to finish parsing and building report).
- If 2_report is chosen, but no previous report_id's are found from a list file (qkview_id_list.json), an warning message will be shown.

```bash
# run script , and call current folder
python3.14 "1_ihealth_submit_and_report.py"
Please enter your selection - Submit QKview to iHealth or Obtain report ( all , 1_submit , 2_report )
all
Please enter folder name to parse QKview files recursively and/or Store Reports in (HINT: may navigate back a folder with ../FOLDERNAME )
../qkview_folder
Please enter iHealth API Username - This should be API Specific not normal Web Username
# OMITTED - iHealth API Username Here
Please enter iHealth API Password - This should be API Specific not normal Web Password
# OMITTED - iHealth API Password Here
Please enter CA location for iHealth
./account-f5-com-chain.pem

# While running some response codes are shown, and a notification if waiting after submission before report retrieval if selection all was made
# When finished current working folder should have a file 'qkview_id_list.json' created if selection all or 1_submit was made
# When finished current working folder should have a file with '[HOSTNAME]_diag_data.json' for each of the qkview file reports obtained if selection all or 2_report was made

❯
```
