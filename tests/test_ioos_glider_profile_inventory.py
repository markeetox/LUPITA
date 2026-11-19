import unittest

from scripts.download_ioos_glider_profile_inventory import (
    normalize_csvp_rows,
    parse_info_variables,
)


class TestErddapInventoryParsing(unittest.TestCase):
    def test_standard_erddap_info_header(self):
        source = """Row Type,Variable Name,Attribute Name,Data Type,Value
attribute,,,,USF Sam
variable,trajectory,,,String
variable,profile_id,,,String
variable,temperature,,,float
"""
        variables, headers = parse_info_variables(source)
        self.assertEqual(variables, ["profile_id", "temperature", "trajectory"])
        self.assertEqual(headers[0], "Row Type")

    def test_legacy_compact_info_header(self):
        source = """rowName,variableName,attributeName,dataType,value
variable,temperature,,float,
variable,depth,,float,
"""
        variables, _ = parse_info_variables(source)
        self.assertEqual(variables, ["depth", "temperature"])

    def test_csvp_headers_with_units_are_normalized(self):
        source = '''trajectory (String),temperature (degree_C),depth (m)
glider-a,18.25,12.5
glider-a,18.5,13.0
'''
        headers, rows = normalize_csvp_rows(source)
        self.assertEqual(headers, ["trajectory", "temperature", "depth"])
        self.assertEqual(rows[0]["temperature"], "18.25")
        self.assertEqual(rows[1]["depth"], "13.0")

    def test_csvp_headers_without_units_are_supported(self):
        source = "temperature,depth\n18.25,12.5\n"
        headers, rows = normalize_csvp_rows(source)
        self.assertEqual(headers, ["temperature", "depth"])
        self.assertEqual(rows[0]["temperature"], "18.25")

    def test_unrecognized_info_header_fails_clearly(self):
        with self.assertRaisesRegex(ValueError, "Unrecognized ERDDAP info CSV header"):
            parse_info_variables("name,type\ntemperature,float\n")

    def test_empty_info_response_fails_clearly(self):
        with self.assertRaisesRegex(ValueError, "empty or has no header"):
            parse_info_variables("")


if __name__ == "__main__":
    unittest.main()
