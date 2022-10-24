"""
Turn txions into Gremlin style GraphML.
Example: https://github.com/tinkerpop/gremlin/blob/master/data/graph-example-1.xml
"""
from dataclasses import dataclass
from functools import partial
from os import path
from typing import Union
from xml.etree import ElementTree as ET

from bs4 import BeautifulSoup
from pympler.asizeof import asizeof

from ethecycle.blockchains import get_chain_info
from ethecycle.graph import is_wallet_in_graph
from ethecycle.export.gremlin_csv import OUTPUT_DIR
from ethecycle.transaction import Txn
from ethecycle.util.logging import console, log
from ethecycle.util.num_helper import MEGABYTE, SIZES, size_string
from ethecycle.util.string_constants import *
from ethecycle.util.types import WalletTxns


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


ObjProperty = partial(GraphObjectProperty, 'all')
NodeProperty = partial(GraphObjectProperty, 'node')
EdgeProperty = partial(GraphObjectProperty, 'edge')

NODE_PROPERTIES = [
    NodeProperty(LABEL_V, 'string'),
]

EDGE_PROPERTIES = [
    EdgeProperty(LABEL_E, 'string'),
    EdgeProperty('num_tokens', 'double'),
    EdgeProperty('block_number', 'int'),
    EdgeProperty('token_address', 'string'),
    EdgeProperty('token', 'string'),
    EdgeProperty('transaction_hash', 'string'),
]

OBJ_PROPERTIES = [
    ObjProperty(SCANNER_URL, 'string')
]

GRAPH_OBJ_PROPERTIES = NODE_PROPERTIES + EDGE_PROPERTIES + OBJ_PROPERTIES
GRAPHML_EXTENSION = '.graph.xml'  # .graphml extension is not recognized by Gremlin
GRAPHML_OUTPUT_FILE = path.join(OUTPUT_DIR, 'nodes.xml')

XML_PROPS = {
    'xmlns': "http://graphml.graphdrawing.org/xmlns",
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
}


def build_graphml(wallets_txns: WalletTxns, blockchain: str) -> ET.ElementTree:
    """Export txions to GraphML format. Graph ID is 'blockchain'. Returns file written."""
    all_txns = [txn for txns in wallets_txns.values() for txn in txns]
    chain_info = get_chain_info(blockchain)
    root = ET.Element('graphml', XML_PROPS)
    wallets_already_in_graph_count = 0

    # <key> elements describe the properties vertices and edges can have.
    for graph_obj_property in GRAPH_OBJ_PROPERTIES:
        root.append(graph_obj_property.to_graphml())

    # Add the <graph>. IMPORTANT: the <key> elements MUST come before the <graph> in the XML.
    graph = ET.SubElement(root, 'graph', {'id': blockchain, 'edgedefault': 'directed'})

    # Wallets are <node> elements. TODO: wallets still don't label correctly...
    wallets = set(wallets_txns.keys()).union(set([txn.to_address for txn in all_txns]))

    for wallet_address in wallets:
        if is_wallet_in_graph(wallet_address):
            log.debug(f"Wallet '{wallet_address}' is already in graph...")
            wallets_already_in_graph_count += 1
            continue

        wallet = ET.SubElement(graph, 'node', {'id': wallet_address})
        _attribute_xml(wallet, LABEL_V, WALLET)
        _attribute_xml(wallet, SCANNER_URL, chain_info.scanner_url(wallet_address))

    # Transactions are <edge> elements.
    for txn in all_txns:
        _add_transaction(graph, txn)

    xml = ET.ElementTree(root)
    console.print(f"Created XML for {len(wallets)} wallet nodes...")
    console.print(f"   (Skipped {wallets_already_in_graph_count} wallets that already existed in graph)", style='dim')
    console.print(f"Created XML for {len(all_txns)} transaction edges...")
    console.print(f"   (In memory size of generated XML: {(size_string(_xml_size(xml)))})", style='dim')
    return xml


def export_graphml(wallets_txns: WalletTxns, blockchain: str, output_path: str) -> str:
    """
    Build graphML data for 'wallets_txns' and write to output_path. Note that output_path must also be
    accessible from the gremlin-server container.
    """
    if not output_path.endswith(GRAPHML_EXTENSION):
        log.warning(f"Forcing graphML output_path '{output_path}' to end in {GRAPHML_EXTENSION}.")
        output_path = output_path + GRAPHML_EXTENSION

    with open(output_path, 'wb') as file:
        graphml = build_graphml(wallets_txns, blockchain)
        console.print(f"Writing graphML to '{output_path}'...")
        graphml.write(file)

    return output_path


def pretty_print_xml_file(xml_file_path: str, force: bool = False) -> None:
    """Pretty print an XML file"""
    file_size = path.getsize(xml_file_path)

    if file_size > MEGABYTE and not force:
        console.print(f"XML file '{xml_file_path}' is {size_string(file_size)}, too big to print for debugging...")
        return

    console.print(BeautifulSoup(open(xml_file_path), 'xml').prettify())


def _add_transaction(graph_xml: ET.Element, txn: Txn) -> ET.Element:
    """Add txn as an edge as a sub element of the <graph> xml element."""
    edge = ET.SubElement(graph_xml, 'edge', _txn_edge_attribs(txn))
    txn.labelE = TXN  # Tag with 'labelE' for convenience of upcoming for loop

    for edge_property in EDGE_PROPERTIES + OBJ_PROPERTIES:
        _attribute_xml(edge, edge_property.name, vars(txn)[edge_property.name])

    return edge


def _txn_edge_attribs(txn: Txn) -> dict:
    """Get the edge properties for a transaction."""
    return {
        'id': txn.transaction_id,
        'label': TXN,
        'source': txn.from_address,
        'target': txn.to_address,
    }


def _attribute_xml(graph_element: ET.Element, attr_name: str, attr_value: Union[float, int, str]):
    """Build the <data> elements that are graph properties."""
    data = ET.SubElement(graph_element, 'data', {'key': attr_name})

    if isinstance(attr_value, int):
        data.text = str(int(attr_value))  # Force non-scientific notation
    elif isinstance(attr_value, float):
        data.text = "{:.18f}".format(attr_value)
    else:
        data.text = attr_value


def _xml_size(xml: ET.ElementTree):
    size = asizeof(xml)

    for element in xml.iter():
        size += asizeof(element)

    return size
