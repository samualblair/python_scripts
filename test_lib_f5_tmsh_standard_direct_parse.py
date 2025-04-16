# Created by: Michael Johnson - 11-21-2024 , Initial idea and structure from nsmcan @DevCentral
# Paring code to filter out information from tmsh bigip.conf file (one-line format)
# See [https:]//community[.]f5[.]com/discussions/technicalforum/any-python-experts-out-there---parsing-tmsh-list/297634

# import required module
import unittest
import lib_f5_tmsh_standard_direct_parse as tmsh_normal

TEST_F5_ONELINE_CONFIG = """ltm node /Common/1.1.1.1 { address 1.1.1.1 description "Example Node A" monitor /Common/icmp }
ltm node /Common/2.2.2.2 { address 2.2.2.2 description "Example Node B" monitor /Common/icmp }"""

TEST_F5_NORMAL_CONFIG = """ltm node /Common/1.1.1.1 {
    address 1.1.1.1
    description "Example Node A"
    monitor /Common/icmp
}
ltm node /Common/2.2.2.2 {
    address 2.2.2.2
    description "Example Node B"
    monitor /Common/icmp
}"""

class TestStringMethods(unittest.TestCase):

    def test_base(self):
        test_f5_oneline_config_lines = TEST_F5_ONELINE_CONFIG.splitlines()
        test_f5_normal_config_converted = tmsh_normal.convert_tmsh_output_to_oneline(TEST_F5_NORMAL_CONFIG)
        self.assertEqual(test_f5_oneline_config_lines, test_f5_normal_config_converted)

    def test_key_value_format(self):
        test_f5_oneline_config_lines = TEST_F5_ONELINE_CONFIG.splitlines()
        test_f5_normal_config_converted = tmsh_normal.convert_tmsh_output_to_oneline(TEST_F5_NORMAL_CONFIG)
        list_oneline = []
        list_normal = []

        for test_f5_oneline_config_line in test_f5_oneline_config_lines:
            test_f5_oneline_config_split = tmsh_normal.parse_tmsh_one_line_output(test_f5_oneline_config_line)
            list_oneline.append(test_f5_oneline_config_split)

        for lines in test_f5_normal_config_converted:
            test_f5_normal_config_split = tmsh_normal.parse_tmsh_one_line_output(lines)
            list_normal.append(test_f5_normal_config_split)
    
        self.assertListEqual(list_oneline,list_normal)

if __name__ == "__main__":
    unittest.main()
