# Created by: Michael Johnson - 04-15-2025
# Paring code to filter out information from tmsh bigip.conf file (standard tmsh format or oneline format)
# Initial idea from nsmcan @DevCentral
# See [https:]//community[.]f5[.]com/discussions/technicalforum/any-python-experts-out-there---parsing-tmsh-list/297634

import json

def parse_layer(tokens:list):
    """
    Parses one dictionary layer from the tokens
    @param tokens: string tokens
    @return: parsed dictionary, leftover tokens
    """
    
    DECLARATIVE_KEYS = ['disabled', 'internal', 'ip-forward', 'vlans-enabled', 'count', 
                        'socks4', 'socks4a', 'socks5', 'avg_tps', 'avg_request_throughput',
                        '__', 'errors', 'drop_count', 'total_attacks_count', 'events_count', 
                        'acl_matches','total_count','psm_protocol_type','FTP', 'SMTP',
                        # GTM Parsing Additions
                        'a', 'http', 'https', 'sip', 'smtp']

    result = {}
    is_key = True  # The first token will be a key
    key = None
    while tokens:
        token = tokens.pop(0)

        if is_key:
            key = token
            if key in DECLARATIVE_KEYS:
                result[key] = True
                continue
            if key == '}':
                #remaining_tokens = len(tokens)
                #if remaining_tokens > 0:
                #    print(tokens)
                break
            is_key = False
        else:
            value = token
            is_key = True
            if value == '{':
                result[key], tokens = parse_layer(tokens)
                continue
            if value.startswith('"'):
                tokens.insert(0, value[1:])
                parts = []
                while tokens:
                    token = tokens.pop(0)
                    if token.endswith('"') and not token.endswith('\\"'):
                        parts.append(token[:-1])
                        break
                    parts.append(token)
                value = ' '.join(parts)
            # Catch value "}"
            # if value == '}':
            #     print('This KEY needs to have a value: '+key)
            result[key] = value.replace('\\"', '"')

    # end while
    return result, tokens

def parse_tmsh_one_line_output(singleline_parse:str):
    """
    Parses output of a tmsh command produced in machine-readable format with the 'one-line' option
    @param singleline_parse: String of Command output
    @return: Parsed dictionary
    """

    _tokens = singleline_parse.split(' ')
    parsed, _ = parse_layer(_tokens)
    #if _:
        #print("Warning There were leftover tokens:")
        #print(_)
    return parsed

def convert_tmsh_output_to_oneline(config_input):
    """
    Parses output of a tmsh config and provides output in a format similar to the 'one-line' option
    @param out: Command output
    @return: List
    """

    list_of_tmsh_lines = []
    current_line = ""
    # current_line_number = 0
    current_start_brace = 0
    # current_end_brace = 0
    char_remaining = len(config_input)
    last_text = ""
    for text in config_input:
        char_remaining = char_remaining - 1
        skip_duplicate_space = False
        if text == " ":
            if last_text == " ":
                last_text = text
                skip_duplicate_space = True
            else:
                last_text = text
                skip_duplicate_space = False
        else:
            last_text = text
            skip_duplicate_space = False

        if skip_duplicate_space:
            # Matches multiple spaces so do not append
            pass
        else:
            if text == "{":
                current_start_brace += 1
            if text == "}":
                current_start_brace -= 1
                if current_start_brace <0:
                    raise IndexError("something is wrong as current start brace is below 0")
            if text == "\n":
                if current_start_brace == 0:
                    # End of current section - add to list of lines
                    list_of_tmsh_lines.append(current_line)
                    current_line = ""
                    last_text = ""
                else:
                    # Replace newline with space only
                    current_line = current_line + " "
                    # Ensure last text entered is recorded properly
                    last_text = " "
            else:
                # Catch edge case for final line if source string does not have trailing \n in it - add to list of lines
                if char_remaining == 0:
                    current_line = current_line + text
                    list_of_tmsh_lines.append(current_line)
                    current_line = ""
                    last_text = ""
                else:
                    current_line = current_line + text
        
    return list_of_tmsh_lines

def print_conversion_normal(bigipconf_filename:str="bigip.conf"):
    
    list_normal = []

    with open(bigipconf_filename, 'r') as bigipconf_configfile:
        
        
        working_file = bigipconf_configfile.read()

        f5_normal_config_converted = convert_tmsh_output_to_oneline(working_file)

        list_normal = []

        for lines in f5_normal_config_converted:
            test_f5_normal_config_split = parse_tmsh_one_line_output(lines)
            list_normal.append(test_f5_normal_config_split)

    with open(bigipconf_filename[:-5]+'_dict.json', 'w') as bigipconf_dict_file:
        json_string = json.dumps(list_normal, indent=4)
        bigipconf_dict_file.write(json_string)
