import unittest

from scripts.download_ioos_glider_profile_inventory import parse_info_variables


class TestErddapInfoVariableParser(unittest.TestCase):
    def test_standard_erddap_header_with_spaces(self):
        source = """Row Type,Variable Name,Attribute Name,Data Type,Value
attribute,,,,USF Sam
variable,trajectory,,,String
variable,profile_id,,,String
variable,temperature,,,float
attribute,temperature,units,String,degree_C
"""
        variables, headers = parse_info_variables(source)
        self.assertEqual(variables, ["profile_id", "temperature", "trajectory"])
        self.assertEqual(headers[0], "Row Type")

    def test_legacy_compact_header(self):
        source = """rowName,variableName,attributeName,dataType,value
variable,temperature,,float,
variable,depth,,float,
attribute,temperature,units,String,degree_C
"""
        variables, _ = parse_info_variables(source)
        self.assertEqual(variables, ["depth", "temperature"])

    def test_unrecognized_header_fails_with_clear_error(self):
        with self.assertRaisesRegex(ValueError, "Unrecognized ERDDAP info CSV header"):
            parse_info_variables("name,type\ntemperature,float\n")

    def test_empty_response_fails_with_clear_error(self):
        with self.assertRaisesRegex(ValueError, "empty or has no header"):
            parse_info_variables("")


if __name__ == "__main__":
    unittest.main()
