# python_scripts

A Collection of Python Scripts - some organized into sub repositories.

## Sub Repositories

### Outlook Email Template (python_outlook_template)
[![python-version](https://img.shields.io/badge/python-3.13.1-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![f5py](https://img.shields.io/badge/appscript-darkblue)](https://appscript.sourceforge.io/py-appscript/index.html)

An email draft will open in outlook, ready for final touches and/or to be sent.

### F5 Extract and Parse Workflow 1 (workflow_1_extract_and_parse)
[![python-version](https://img.shields.io/badge/python-3.13.1-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![f5py](https://img.shields.io/badge/f5py-0.3.0-red)](https://pypi.org/project/f5py)

Extracts F5 configuration from F5 Qkview file.

Convert to JSON for easier parsing.

Parse config and output no SNAT Virtual Servers

Continue to parse previous output and output no SNAT details summary

### F5 Extract and Parse Workflow 2 (workflow_2_extract_merge_combine)
[![python-version](https://img.shields.io/badge/python-3.13.1-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

Extracts F5 configuration and Certificates from F5 Qkview, UCS, or generic tar.gz file.

Modifes BigDB.dat files to support VE licensing.

Organize and assist with merging.

TODO: Directly assist with merging.

Assist with Re-Archiving.

## Others
[![python-version](https://img.shields.io/badge/python-3.13.1-blue)](https://www.python.org/downloads/)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)
[![f5py](https://img.shields.io/badge/f5py-0.3.0-red)](https://pypi.org/project/f5py)

F5 AS3 Parsing

F5 Convert to JSON for easier parsing

F5 Extract configs from Qkview file all configuration

F5 Extract no snat configs and produce summary

F5 Parse bigip.conf (normal and oneline) to dictionary format

## Authors
Michael Johnson ([@samualblair](https://github.com/samualblair))

## Versioning
[![CalVer](https://img.shields.io/static/v1?label=CalVer&message=YY.0M.0D)](https://calver.org/)

* 2025.04.21 - BugFix - Enclosed filepath/name in quotes to allow for space and other special characters for workflow 1, workflow 2, and extract
* 2025.04.17 - Added Script for extract, modify BigDB.dat, and re-archive script for workflow 2
* 2025.04.15 - Added BigIP tmsh to Dictionary parsing script
* 2025.04.08 - Added BigDB.dat modify for VE change script to workflow 2
* 2025.04.07 - Folder recursion Fixes
* 2025.04.03 - Addition of workflow 2
* 2025.04.02 - Compare and Except refactoring, added UCS support for extracting bigip configs
* 2025.02.05 - Addition of outlook template
* 2025.01.21 - General release
* Pre-release development
