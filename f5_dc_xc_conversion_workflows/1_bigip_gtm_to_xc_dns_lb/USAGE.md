# F5 BIG-IP TMSH GTM to F5 DC (XC) DNS-LB

This workflow has 3-4 steps, to convert and deliver (optionally) or backup (optionally) a BIG-IP GTM to F5 DC (XC) DNS-LB.
1) Convert from TMSH config to Initial JSON (just for a structured data version of TMSH config)
2) Heavy conversion, preparing F5 XC API JSON files and CSV for Review
3) Deliver New Configurations to F5 XC via API
4) Backup F5 XC via API, using list of entires that would otherwise be configured

Output files after the 2nd step help for review, and adjustment if required.
Some changes may be needed to script in 2nd step if custom logic is required.

## Script Overviews

### Script 1 Overview: 

- Looks in destination folder, and subfolders for compressed files for any gtm.conf file.
- Converts produces a 'FILENAME + _dict.json'

### Script 2 Overview:

- Opens a single file provided (EXAMPLE: pythong3 2_bigip_gtm_to_f5dc_xc_conversion.py FILENAME_dict.json)
- Converts into custom Dictionary (object oriented), creates a 'FILENAME + _converted.json' for review.
- Creates CSV with key information 'FILENAME + _converted.csv' for review.
- Generates F5-XC Ready API JSON Files, based off Jinja Templates in folder ./xc_api_templates , rendered into ./jinja_rendered

### Script 3 Overview:

- Delivers (in order) files from folder ./jinja_rendered to F5 XC via API calls (configuring DNS-LB, all elements).

### Script 4 Overview:

- Obtains current configuration to perform backup (in order) files from folder ./jinja_rendered from F5 XC via API calls (obtains backup for DNS-LB, all elements matching).

## Usage Example for Script 1:
```bash
#TBD
```

## Usage Example for Script 2:
```bash
#TBD
```

## Usage Example for Script 3:
```bash
#TBD
```

## Usage Example for Script 4:
```bash
#TBD
```