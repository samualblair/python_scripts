# F5 Extract and Parse Workflow 1
[![python-version](https://img.shields.io/badge/python-3.13.1-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Looks in destination folder for config files to convert.
Convert to JSON for easier parsing.

## Work in progress but initial options are:

### Option 1 - very functinoal for gtm, somewhat functional for other modules
* run '1_f5_tmsh_to_json_dict_using_convert_lib' , That calls 'lib_f5_tmsh_standard_direct_parse' an produces an output conversion in json (set of configuration objects with key-value pairs)
* Use this file as needed

### Option 2 - very functinoal for gtm , still in progress for tlm
* run '1_f5_tmsh_to_json_dict_using_convert_lib' , That calls 'lib_f5_tmsh_standard_direct_parse' an produces an output conversion in json (set of configuration objects with key-value pairs)
* run a follow-up script for GTM, LTM, or other
  * For GTM - '2_bigip_gtm_to_f5dc_xc_conversion' 
    * This starts by processing and converts GTM configuration into a dictionary that is organized by object name (GMT related objects) - also can save as json export (custom)
    * This continues by converting into a format for F5 DC (XC) , generating F5 XC API based JSON Configurations
    * Currently Requires - Jinja2 , looking to seperate that out as optional requirement
  * For LTM - 'bigip_ltm_to_object_name_conversion' 
    * This starts by processing and converts LTM configuration into a dictionary that is organized by object name (LTM related objects) - also can save as json export (custom)
  * Deliver or Build Reports from Data
    * f5_xc_deliver_dns_lb_configurations -> For GTM to XC conversions - Deliver configurations to XC. Requires 'requests' library for HTTP calls.
    * TBD -> For LTM , build reports

### Option 3 - this option is not fully baked - different format than option 2 right now
* Using 'f5_tmsh_convert_to_json_folder_recursive' to create a better formatted dictionary and json right away
* Use this better formatted dictionary and/or json as needed for further processing


## Usage Example for Script 1:
```bash
#TBD
```

## Authors
Michael Johnson ([@samualblair](https://github.com/samualblair))

## Versioning
[![CalVer](https://img.shields.io/static/v1?label=CalVer&message=YY.0M.0D)](https://calver.org/)

* 2025.09.29 - First General release
* Pre-release development
