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
from os import path
from typing import Dict, List
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

from ethecycle.export.gremlin_csv import OUTPUT_DIR
from ethecycle.logging import console
from ethecycle.transaction import Txn
from ethecycle.util.string_constants import *

GRAPHML_OUTPUT_FILE = path.join(OUTPUT_DIR, 'nodes.xml')

TXN_PROPERTIES = {
    'value': 'double',  # number_of_tokens
    'block_number': 'int',
    #'token': 'string',  # TODO: write the token name (e.g. 'USDT')
    #'address': 'string'
    'token_address': 'string'
}

COMMON_PROPERTIES = {
    'labelV': 'string',
    'labelE': 'string'
}

ALL_PROPERTIES = TXN_PROPERTIES.copy()
ALL_PROPERTIES.update(COMMON_PROPERTIES)

XML_PROPS = {
    'xmlns': "http://graphml.graphdrawing.org/xmlns",
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
}

property_id = lambda i: f"d{i}"


def export_graphml(wallets_addresses: Dict[str, List[Txn]], blockchain: str) -> str:
    """Export txions to GraphML format. graph_id shouold be """
    root = ET.Element('graphml', XML_PROPS)
    graph = ET.SubElement(root, 'graph', {'id': blockchain, 'edgedefault': 'directed'})

    # Describe the properties our vertices or edges will have.
    # TODO: remove enumerate
    for i, (attribute, attribute_type) in enumerate(ALL_PROPERTIES.items()):
        ET.SubElement(
            root,
            'key',
            {'id': attribute, 'for': 'all', 'attr.name': attribute, 'attr.type': attribute_type}
        )

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

            # TODO: remove enumerate
            for i, property in enumerate(TXN_PROPERTIES.keys()):
                data = ET.SubElement(edge, 'data', {'key': property})

                if property == 'value':
                    data.text = txn.value_str
                else:
                    value = vars(txn)[property]
                    data.text = str(value)

    #root.append(graph)
    tree = ET.ElementTree(root)

    with open(GRAPHML_OUTPUT_FILE, "wb") as files:
        tree.write(files)

    return GRAPHML_OUTPUT_FILE


def pretty_print_xml():
    console.print(BeautifulSoup(open(GRAPHML_OUTPUT_FILE), 'xml').prettify())
