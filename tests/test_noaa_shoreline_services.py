import xml.etree.ElementTree as ET

from scripts.audit_noaa_shoreline_services import (
    is_candidate,
    parse_feature_types,
    parse_wms_layers,
)


def test_parse_wfs_feature_types_and_candidate_layers():
    xml = """<wfs:WFS_Capabilities xmlns:wfs="http://www.opengis.net/wfs/2.0">
      <wfs:FeatureTypeList>
        <wfs:FeatureType>
          <wfs:Name>nsde:National_Shoreline</wfs:Name>
          <wfs:Title>National Shoreline</wfs:Title>
          <wfs:DefaultCRS>urn:ogc:def:crs:EPSG::4269</wfs:DefaultCRS>
        </wfs:FeatureType>
        <wfs:FeatureType>
          <wfs:Name>nsde:Imagery_Index</wfs:Name>
          <wfs:Title>Imagery footprints</wfs:Title>
        </wfs:FeatureType>
      </wfs:FeatureTypeList>
    </wfs:WFS_Capabilities>"""
    layers = parse_feature_types(xml)
    assert len(layers) == 2
    assert layers[0]["Name"] == "nsde:National_Shoreline"
    assert is_candidate(layers[0])
    assert not is_candidate(layers[1])


def test_parse_wms_layers_ignores_parent_without_name():
    xml = """<WMS_Capabilities xmlns="http://www.opengis.net/wms">
      <Capability><Layer><Title>Root</Title>
        <Layer><Name>nsde:cusp_shoreline</Name><Title>CUSP Shoreline</Title></Layer>
        <Layer><Name>nsde:imagery</Name><Title>Imagery</Title></Layer>
      </Layer></Capability>
    </WMS_Capabilities>"""
    layers = parse_wms_layers(xml)
    assert len(layers) == 2
    assert layers[0]["Name"] == "nsde:cusp_shoreline"
    assert is_candidate(layers[0])
    assert not is_candidate(layers[1])
