"""
Turn txions into Gremlin style GraphML.
Example: https://github.com/tinkerpop/gremlin/blob/master/data/graph-example-1.xml
"""
import time
from dataclasses import dataclass
from functools import partial
from os import path
from typing import List, Union

from bs4 import BeautifulSoup
from lxml import etree
from pympler.asizeof import asizeof

from ethecycle.blockchains.blockchains import get_chain_info
from ethecycle.config import Config
#from ethecycle.graph import is_wallet_in_graph
from ethecycle.models.transaction import Txn
from ethecycle.util.logging import console, log
from ethecycle.util.number_helper import MEGABYTE, size_string
from ethecycle.util.string_constants import *
from ethecycle.util.types import WalletTxns


class GraphPropertyManager:
    @dataclass
    class GraphObjectProperty:
        obj_type: str
        name: str
        data_type: str

        def to_graphml(self) -> etree._Element:
            """Construct <key> XML element."""
            return etree.Element(
                'key',
                **{'id': self.name, 'for': self.obj_type, 'attr.name': self.name, 'attr.type':self.data_type}
            )

    ObjProperty = partial(GraphObjectProperty, 'all')
    NodeProperty = partial(GraphObjectProperty, 'node')
    EdgeProperty = partial(GraphObjectProperty, 'edge')

    ALL_OBJ_PROPERTIES = [
        ObjProperty(SCANNER_URL, 'string')
    ]

    NODE_PROPERTIES = [
        NodeProperty(LABEL_V, 'string'),
    ]

    EDGE_PROPERTIES = [
        EdgeProperty(LABEL_E, 'string'),
        EdgeProperty('num_tokens', 'double'),
        EdgeProperty('block_number', 'int'),
        EdgeProperty('token_address', 'string'),
        EdgeProperty('token', 'string'),
    ]

    EXTENDED_NODE_PROPERTIES = ALL_OBJ_PROPERTIES + NODE_PROPERTIES

    EXTENDED_EDGE_PROPERTIES = ALL_OBJ_PROPERTIES + EDGE_PROPERTIES + [
        EdgeProperty('blockchain', 'string'),
        EdgeProperty('transaction_hash', 'string'),
    ]

    @classmethod
    def node_properties(cls) -> List[GraphObjectProperty]:
        if Config.include_extended_properties:
            return cls.EXTENDED_NODE_PROPERTIES
        else:
            return cls.NODE_PROPERTIES

    @classmethod
    def edge_properties(cls) -> List[GraphObjectProperty]:
        if Config.include_extended_properties:
            return cls.EXTENDED_EDGE_PROPERTIES
        else:
            return cls.EDGE_PROPERTIES

    @classmethod
    def all_obj_properties(cls) -> List[GraphObjectProperty]:
        if Config.include_extended_properties:
            return cls.EXTENDED_EDGE_PROPERTIES + cls.NODE_PROPERTIES
        else:
            return cls.EDGE_PROPERTIES + cls.NODE_PROPERTIES


GRAPHML_EXTENSION = '.graph.xml'  # .graphml extension is not recognized by Gremlin

# Gremlin puts these props in its exported <graphml> but they don't seem to be necessary
# (which is good because lxml doesn't like them).
XML_PROPS = {
    'xmlns': "http://graphml.graphdrawing.org/xmlns",
    'xmlns:xsi': "http://www.w3.org/2001/XMLSchema-instance",
    'xsi:schemaLocation': "http://graphml.graphdrawing.org/xmlns http://graphml.graphdrawing.org/xmlns/1.0/graphml.xsd",
}


def build_graphml(wallets_txns: WalletTxns, blockchain: str) -> etree._ElementTree:
    """Export txions to GraphML format. Graph ID is 'blockchain'. Returns file written."""
    all_txns = [txn for txns in wallets_txns.values() for txn in txns]
    chain_info = get_chain_info(blockchain)
    root = etree.Element('graphml')#, **XML_PROPS)
    wallets_already_in_graph_count = 0

    # <key> elements describe the properties vertices and edges can have.
    for graph_obj_property in GraphPropertyManager.all_obj_properties():
        root.append(graph_obj_property.to_graphml())

    # Add the <graph>. IMPORTANT: the <key> elements MUST come before the <graph> in the XML.
    graph = etree.SubElement(root, 'graph', **{'id': blockchain, 'edgedefault': 'directed'})

    # Wallets are <node> elements. TODO: wallets still don't label correctly...
    wallets = set(wallets_txns.keys()).union(set([txn.to_address for txn in all_txns]))

    for wallet_address in wallets:
        # Commented out because until we have a way to actually totally bisect the graph this is an
        # unnecessary cost.
        # if is_wallet_in_graph(wallet_address):
        #     log.debug(f"Wallet '{wallet_address}' is already in graph...")
        #     wallets_already_in_graph_count += 1
        #     continue

        wallet = etree.SubElement(graph, 'node', **{'id': wallet_address})
        _attribute_xml(wallet, LABEL_V, WALLET)

        if Config.include_extended_properties:
            _attribute_xml(wallet, SCANNER_URL, chain_info.scanner_url(wallet_address))

    # Transactions are <edge> elements.
    for txn in all_txns:
        _add_transaction(graph, txn)

    xml = etree.ElementTree(root)
    console.print(f"Created XML for {len(wallets)} wallet nodes...")
    console.print(f"Created XML for {len(all_txns)} transaction edges...")
    console.print(f"   Skipped {wallets_already_in_graph_count} wallets already extant in graph...", style='dim')
    console.print(f"   Estimated in memory size of generated XML: {(size_string(_xml_size(xml)))}", style='dim')
    return xml


def export_graphml(
        wallets_txns: WalletTxns,
        blockchain: str,
        output_path: str
    ) -> str:
    """
    Build graphML data for 'wallets_txns' and write to output_path. Note that output_path must also be
    accessible from the gremlin-server container.
    """
    if not output_path.endswith(GRAPHML_EXTENSION):
        log.warning(f"Forcing graphML output_path '{output_path}' to end in {GRAPHML_EXTENSION}.")
        output_path = output_path + GRAPHML_EXTENSION

    start_time = time.perf_counter()
    graphml = build_graphml(wallets_txns, blockchain)
    transform_duration = time.perf_counter() - start_time
    console.print(f"   Transformed to in memory graphML in {transform_duration:02.2f} seconds...", style='benchmark')

    with open(output_path, 'wb') as file:
        console.print(f"Writing graphML to '{output_path}'...")
        graphml.write(file)
        write_duration = time.perf_counter() - transform_duration - start_time
        console.print(f"   Wrote graphML to disk in {write_duration:02.2f} seconds...", style='benchmark')

    return output_path


def pretty_print_xml_file(xml_file_path: str, force: bool = False) -> None:
    """Pretty print an XML file"""
    file_size = path.getsize(xml_file_path)

    if file_size > MEGABYTE and not force:
        console.print(f"XML file '{xml_file_path}' is {size_string(file_size)}, too big to print for debugging...")
        return

    console.print(BeautifulSoup(open(xml_file_path), 'xml').prettify())


def _add_transaction(graph_xml: etree._Element, txn: Txn) -> etree._Element:
    """Add txn as an edge as a sub element of the <graph> xml element."""
    edge = etree.SubElement(graph_xml, 'edge', **_txn_edge_attribs(txn))
    txn.labelE = TXN  # Tag with 'labelE' for convenience of upcoming for loop

    for edge_property in GraphPropertyManager.edge_properties():
        property_value = vars(txn)[edge_property.name]

        if property_value:
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


def _attribute_xml(graph_element: etree._Element, attr_name: str, attr_value: Union[float, int, str]):
    """Build the <data> elements that are graph properties."""
    data = etree.SubElement(graph_element, 'data', **{'key': attr_name})

    if isinstance(attr_value, int):
        data.text = str(int(attr_value))  # Force non-scientific notation
    elif isinstance(attr_value, float):
        data.text = "{:.18f}".format(attr_value)
    else:
        data.text = attr_value


def _xml_size(xml: etree._ElementTree):
    size = asizeof(xml)

    for element in xml.iter():
        size += asizeof(element)

    return size
