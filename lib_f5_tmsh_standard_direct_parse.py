# Created by: Michael Johnson - 11-21-2024
# Paring code to filter out information from tmsh bigip.conf file (standard tmsh format or oneline format)
# Initial idea from nsmcan @DevCentral
# See [https:]//community[.]f5[.]com/discussions/technicalforum/any-python-experts-out-there---parsing-tmsh-list/297634

declarative_keys = ['disabled', 'internal', 'ip-forward', 'vlans-enabled']

def parse_tmsh_one_line_output(out):
    """
    Parses output of a tmsh command produced in machine-readable format with the 'one-line' option
    @param out: Command output
    @return: Parsed dictionary
    """
    def parse_layer(tokens):
        """
        Parses one dictionary layer from the tokens
        @param list tokens: string tokens
        @return: parsed dictionary, leftover tokens
        """
        result = {}
        is_key = True  # The first token will be a key
        key = None
        while tokens:
            token = tokens.pop(0)

            if is_key:
                key = token
                if key in declarative_keys:
                    result[key] = True
                    continue
                if key == '}':
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
                result[key] = value.replace('\\"', '"')

        # end while
        return result, tokens

    _tokens = out.split(' ')
    parsed, _ = parse_layer(_tokens)
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
