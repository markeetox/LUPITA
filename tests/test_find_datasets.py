from pipeline import find_datasets as f

SEARCH = '''Title,Summary,FGDC,ISO 19115,Info,Background Info,RSS,Email,Institution,Dataset ID
"Chlorophyll, VIIRS, Daily","...",,,,,,,NOAA,nesdisVHNSQchlaDaily
"All datasets","...",,,,,,,ERDDAP,allDatasets
'''
INFO = '''Row Type,Variable Name,Attribute Name,Data Type,Value
attribute,NC_GLOBAL,time_coverage_end,String,2026-10-08T12:00:00Z
attribute,NC_GLOBAL,time_coverage_start,String,2012-01-02T12:00:00Z
attribute,time,units,String,seconds since 1970-01-01T00:00:00Z
'''


def test_parse_search_skips_all_datasets():
    assert f.parse_search(SEARCH) == [{"id": "nesdisVHNSQchlaDaily", "title": "Chlorophyll, VIIRS, Daily"}]


def test_parse_coverage():
    assert f.parse_coverage(INFO) == {"start": "2012-01-02T12:00:00Z", "end": "2026-10-08T12:00:00Z"}
