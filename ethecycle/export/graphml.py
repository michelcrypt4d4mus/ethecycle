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
    <edge id="e6" source="n5" target="n4">
      <data key="d1">1.1</data>
    </edge>
  </graph>
</graphml>
"""
from dataclasses import dataclass
from functools import partial
from os import path
from typing import Dict, List
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

from ethecycle.export.gremlin_csv import OUTPUT_DIR
from ethecycle.logging import console
from ethecycle.transaction import Txn
from ethecycle.util.string_constants import *


@dataclass
class GraphObjectProperty:
    obj_type: str
    name: str
    data_type: str

    def to_graphml(self, root: ET.Element) -> ET.Element:
        """Attach as a subelement to root object"""
        return ET.SubElement(
            root,
            'key',
            {'id': self.name, 'for': self.data_type, 'attr.name': self.name, 'attr.type':self.data_type}
        )


NodeProperty = partial(GraphObjectProperty, 'node')
EdgeProperty = partial(GraphObjectProperty, 'edge')

GRAPHML_OUTPUT_FILE = path.join(OUTPUT_DIR, 'nodes.xml')

NODE_PROPERTIES = [
    NodeProperty('labelV', 'string')
]

EDGE_PROPERTIES = [
    EdgeProperty('labelE', 'string'),
    EdgeProperty('value', 'double'),
    EdgeProperty('block_number', 'int'),
    EdgeProperty('token_address', 'string'),
]

GRAPH_OBJ_PROPERTIES = EDGE_PROPERTIES + NODE_PROPERTIES

XML_PROPS = {
    'xmlns': "http://graphml.graphdrawing.org/xmlns",
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
}


def export_graphml(wallets_addresses: Dict[str, List[Txn]], blockchain: str) -> str:
    """Export txions to GraphML format. graph_id shouold be """
    root = ET.Element('graphml', XML_PROPS)
    graph = ET.SubElement(root, 'graph', {'id': blockchain, 'edgedefault': 'directed'})

    # Describe the properties our vertices or edges will have.
    for graph_obj_property in GRAPH_OBJ_PROPERTIES:
        graph_obj_property.to_graphml(root)

    # Export wallets as vertices (IDs are the integer version of the hex address)
    for wallet_address in wallets_addresses.keys():
        wallet_node = ET.SubElement(graph, 'node', {'id': wallet_address})
        label = ET.SubElement(wallet_node, 'data', {'key': LABEL_V})
        label.text = WALLET

    # Export txions as edges
    for txions in wallets_addresses.values():
        for txn in txions:
            txn_attribs = {'id': txn.transaction_id, 'source': txn.from_address, 'target': txn.to_address}
            edge = ET.SubElement(graph, 'edge', txn_attribs)
            label = ET.SubElement(edge, 'data', {'key': LABEL_E})
            label.text = TXN

            for edge_property in EDGE_PROPERTIES:
                if edge_property.name == LABEL_E:
                    continue

                data = ET.SubElement(edge, 'data', {'key': edge_property.name})

                if edge_property.name == 'value':
                    data.text = txn.value_str
                else:
                    data.text = str(edge_property.name)

    #root.append(graph)
    tree = ET.ElementTree(root)

    with open(GRAPHML_OUTPUT_FILE, "wb") as files:
        tree.write(files)

    return GRAPHML_OUTPUT_FILE


def pretty_print_xml():
    console.print(BeautifulSoup(open(GRAPHML_OUTPUT_FILE), 'xml').prettify())
