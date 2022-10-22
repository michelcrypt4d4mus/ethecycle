"""
http://graphml.graphdrawing.org/primer/graphml-primer.html

<?xml version="1.0" encoding="UTF-8"?>
<graphml xmlns="http://graphml.graphdrawing.org/xmlns" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd">
  <key id="d0" for="node" attr.name="color" attr.type="string">
    <default>yellow</default>
  </key>
  <key id="d1" for="edge" attr.name="weight" attr.type="double"/>

  <graph id="G" edgedefault="undirected">
    <node id="n0">
      <data key="d0">green</data>
    </node>
    <node id="n1"/>

    <edge id="e3" source="n3" target="n2"/>
    <edge id="e4" source="n2" target="n4"/>
    <edge id="e5" source="n3" target="n5"/>
    <edge id="e6" source="n5" target="n4">
      <data key="d1">1.1</data>
    </edge>
  </graph>
</graphml>
"""

from os import path
from typing import Dict, List
from xml.etree import ElementTree as ET

from ethecyle.export.gremlin_csv import OUTPUT_DIR
from ethecyle.transaction import Txn

PROPERTIES = {
    'value': 'double',  # number_of_tokens
    'block_number': 'int',
    #'token': 'string',
    'token_address': 'string'
}

XML_PROPS = {
    'xmlns': "http://graphml.graphdrawing.org/xmlns",
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
}


def export_xml(wallets_addresses: Dict[str, List[Txn]]) :
    root = ET.Element('graphml', XML_PROPS)

    for i, (attribute, attribute_type) in enumerate(PROPERTIES.items()):
        #root.append(
            ET.SubElement(
                root,
                'key',
                {'id': f"d{i}", 'for': 'node', 'attr.name': attribute, 'attr.type': attribute_type}
            )
        #)

    graph = ET.SubElement(root, 'graph')

    for wallet_address in wallets_addresses.keys():
        node = ET.SubElement(graph, 'node', {'id': wallet_address})

    for txions in wallets_addresses.values():
        for txn in txions:
            txn_attribs = {'id': txn.transaction_id, 'source': txn.from_address, 'target': txn.to_address}
            edge = ET.SubElement(graph, 'edge', txn_attribs)

            for i, property in enumerate(PROPERTIES.keys()):
                data = ET.SubElement(edge, 'data', {'key': f"d{i}"})
                data.text = str(vars(txn)[property])

    root.append(graph)
    tree = ET.ElementTree(root)

    with open(path.join(OUTPUT_DIR, 'nodes.xml'), "wb") as files:
        tree.write(files)
