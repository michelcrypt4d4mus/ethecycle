"""
Turn txions into Gremlin style GraphML.
Example: https://github.com/tinkerpop/gremlin/blob/master/data/graph-example-1.xml
"""
from dataclasses import dataclass
from functools import partial
from os import path
from typing import Dict, List
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup

from ethecycle.export.gremlin_csv import OUTPUT_DIR
from ethecycle.util.logging import console
from ethecycle.transaction import Txn
from ethecycle.util.string_constants import *

GRAPHML_OUTPUT_FILE = path.join(OUTPUT_DIR, 'nodes.xml')

XML_PROPS = {
    'xmlns': "http://graphml.graphdrawing.org/xmlns",
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
}


@dataclass
class GraphObjectProperty:
    obj_type: str
    name: str
    data_type: str

    def to_graphml(self) -> ET.Element:
        """Attach as a subelement to root object"""
        return ET.Element(
            'key',
            {'id': self.name, 'for': self.obj_type, 'attr.name': self.name, 'attr.type':self.data_type}
        )


NodeProperty = partial(GraphObjectProperty, 'node')
EdgeProperty = partial(GraphObjectProperty, 'edge')

NODE_PROPERTIES = [
    # NodeProperty('labelV', 'string')
]

EDGE_PROPERTIES = [
    # EdgeProperty('labelE', 'string'),
    EdgeProperty('value', 'double'),
    EdgeProperty('block_number', 'int'),
    EdgeProperty('token_address', 'string'),
    EdgeProperty('token', 'string'),
    EdgeProperty('transaction_hash', 'string'),
]

GRAPH_OBJ_PROPERTIES = EDGE_PROPERTIES + NODE_PROPERTIES


def export_graphml(wallets_addresses: Dict[str, List[Txn]], blockchain: str) -> str:
    """Export txions to GraphML format. Graph ID is 'blockchain'. Returns file written."""
    root = ET.Element('graphml', XML_PROPS)

    # <key> elements describe the properties vertices and edges can have.
    for graph_obj_property in GRAPH_OBJ_PROPERTIES:
        root.append(graph_obj_property.to_graphml())

    # Add the <graph>. Note that the <key> elements MUST come before the <graph>.
    graph = ET.SubElement(root, 'graph', {'id': blockchain, 'edgedefault': 'directed'})

    # Wallets are <node> elements.
    for wallet_address in wallets_addresses.keys():
        wallet_node = ET.SubElement(graph, 'node', {'id': wallet_address, 'label': WALLET})

    # Transactions are <edge> elements.
    for txions in wallets_addresses.values():
        for txn in txions:
            _add_transaction(graph, txn)

    with open(GRAPHML_OUTPUT_FILE, "wb") as file:
        ET.ElementTree(root).write(file)

    return GRAPHML_OUTPUT_FILE


def pretty_print_xml():
    console.print(BeautifulSoup(open(GRAPHML_OUTPUT_FILE), 'xml').prettify())


def _add_transaction(graph_xml: ET.Element, txn: Txn) -> ET.Element:
    """Add txn as an edge as a sub element of the <graph> xml element."""
    edge = ET.SubElement(graph_xml, 'edge', _txn_edge_attribs(txn))

    for edge_property in EDGE_PROPERTIES:
        data = ET.SubElement(edge, 'data', {'key': edge_property.name})
        data.text = txn.value_str if edge_property.name == 'value' else str(vars(txn)[edge_property.name])

    return edge


def _txn_edge_attribs(txn: Txn) -> dict:
    """Get the edge properties for a transaction."""
    return {
        'id': txn.transaction_id,
        'label': TXN,
        'source': txn.from_address,
        'target': txn.to_address,
    }
