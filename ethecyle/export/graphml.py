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

from ethecyle.export.gremlin_csv import OUTPUT_DIR
from ethecyle.logging import console
from ethecyle.transaction import Txn

GRAPHML_OUTPUT_FILE = path.join(OUTPUT_DIR, 'nodes.xml')

PROPERTIES = {
    'value': 'double',  # number_of_tokens
    'block_number': 'int',
    #'token': 'string',  # TODO: write the token name (e.g. 'USDT')
    #'address': 'string'
    'token_address': 'string'
}

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
    for i, (attribute, attribute_type) in enumerate(PROPERTIES.items()):
        ET.SubElement(
            root,
            'key',
            {'id': property_id(i), 'for': 'all', 'attr.name': attribute, 'attr.type': attribute_type}
        )

    # Export wallets as vertices (IDs are the integer version of the hex address)
    for wallet_address in wallets_addresses.keys():
        wallet_node = ET.SubElement(graph, 'node', {'id': wallet_address})
        #data = ET.SubElement(wallet_node, 'data', {'key': })

    # Export txions as edges
    for txions in wallets_addresses.values():
        for txn in txions:
            txn_attribs = {'id': txn.transaction_id, 'source': txn.from_address, 'target': txn.to_address}
            edge = ET.SubElement(graph, 'edge', txn_attribs)

            for i, property in enumerate(PROPERTIES.keys()):
                data = ET.SubElement(edge, 'data', {'key': property_id(i)})
                value = vars(txn)[property]

                if isinstance(value, int):
                    data.text = str(int(value))
                else:
                    data.text = str(value)

    #root.append(graph)
    tree = ET.ElementTree(root)

    with open(GRAPHML_OUTPUT_FILE, "wb") as files:
        tree.write(files)

    return GRAPHML_OUTPUT_FILE


def pretty_print_xml():
    console.print(BeautifulSoup(open(GRAPHML_OUTPUT_FILE), 'xml').prettify())
