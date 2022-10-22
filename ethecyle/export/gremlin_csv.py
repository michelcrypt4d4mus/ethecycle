"""
Vertices:
    ~id, name:String, age:Int, lang:String, interests:String[], ~label
    v1, "marko", 29, , "sailing;graphs", person
    v2, "lop", , "java", , software

Edges:
    ~id, ~from, ~to, ~label, weight:Double
    e1, v1, v2, created, 0.4
"""
import csv
from os.path import dirname, join, pardir, realpath
from typing import Dict, List

from ethecyle.transaction import ADDRESS, TXN, WALLET, Txn

OUTPUT_DIR = realpath(join(dirname(__file__), pardir, pardir, 'output'))
VERTEX_HEADER = ['~id', '~label']

TRANSACTION_HEADER = [
    '~id',
    '~from',
    '~to',
    '~label',
    'number_of_tokens:Double',
    'block_number:Int',
    'token:String'
]


def export_vertices(wallet_addresses: List[str]) -> None:
    with open(join(OUTPUT_DIR, 'wallets.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(VERTEX_HEADER)

        for wallet in wallet_addresses:
            writer.writerow([wallet, WALLET])


def export_edges(txns: List[Txn]) -> None:
    with open(join(OUTPUT_DIR, 'transactions.csv'), 'w', newline='') as csvfile:
        writer = csv.writer(csvfile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(TRANSACTION_HEADER)

        for txn in txns:
            writer.writerow([
                txn.transaction_id,
                txn.from_address,
                txn.to_address,
                WALLET,
                txn.value,
                txn.block_number,
                txn.token_address
            ])
