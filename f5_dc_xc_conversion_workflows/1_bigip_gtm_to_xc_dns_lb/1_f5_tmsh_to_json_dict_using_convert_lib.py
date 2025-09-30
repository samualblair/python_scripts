# Created by: Michael Johnson - 04-15-2025 , Initial idea and structure from nsmcan @DevCentral
# Paring code to filter out information from tmsh bigip.conf file (one-line format)
# See [https:]//community[.]f5[.]com/discussions/technicalforum/any-python-experts-out-there---parsing-tmsh-list/297634

# import required module
import lib_f5_tmsh_standard_direct_parse as tmsh_normal
import sys

if __name__ == "__main__":
    # print(sys.argv[1])
    try:
        tmsh_normal.print_conversion_normal(sys.argv[1])
    # Catch when file is not parsable UTF 8 or similar
    except UnicodeDecodeError:
        print('Fail to read file - ' + sys.argv[1] + ' : Is this a file to be read?')
    except IndexError:
        tmsh_normal.print_conversion_normal()
