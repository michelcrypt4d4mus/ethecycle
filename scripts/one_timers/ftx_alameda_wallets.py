from ethecycle.chain_addresses.scripts import generate_dune_analytics_where_clause
from ethecycle.models.wallet import Wallet
from ethecycle.util.logging import console, indent_whitespace
from ethecycle.util.string_constants import *
from ethecycle.util.string_helper import quoted_join

from rich.panel import Panel
from rich.pretty import pprint

INDENT = indent_whitespace(2)
wallets = generate_dune_analytics_where_clause(ETHEREUM, ['ftx', 'alameda'])

wallets = [
    w for w in wallets
    if 'NFT' not in w['name'] \
        and w['name'] not in ['@DakotaLameda', '@TanjaLameda', 'BoycottFTX', 'Binance Wallet for FTX Token ($FTT)', '@ftxjqbhmgv5707']
]

wallets = sorted(wallets, key=lambda w: w['name'])
pprint(wallets)

console.print(Panel('Query WHERE clause'))
addresses = [f"'{w[ADDRESS]}',   -- {w[NAME]}" for w in wallets]
sql = f"\n{INDENT}".join(addresses)
print(f"address IN (\n{INDENT}{sql}\n)")



# Test the addresses shown on Dune
ALAMEDA =[
    '0xe31a9498a22493ab922bc0eb240313a46525ee0a',
    '0x712d0f306956a6a4b4f9319ad9b9de48c5345996',
    '0x93c08a3168fc469f3fc165cd3a471d19a37ca19e',
    '0xca436e14855323927d6e6264470ded36455fc8bd',
    '0x83a127952d266a6ea306c40ac62a4a70668fe3bd',
    '0xc5ed2333f8a2c351fca35e5ebadb2a82f5d254c3',
    '0x89183c0a8965c0299997be9af700a801bdccc2da',
    '0xe5d0ef77aed07c302634dc370537126a2cd26590',
    '0x5d13f4bf21db713e17e04d711e0bf7eaf18540d6',
    '0x882a812d75aee53efb8a144f984b258b6c4807f0',
    '0xbefe4f86f189c1c817446b71eb6ac90e3cb68e60',
    '0xb78e90e2ec737a2c0a24d68a0e54b410fff3bd6b',
    '0x964d9d1a532b5a5daeacbac71d46320de313ae9c',
    '0xfa453aec042a837e4aebbadab9d4e25b15fad69d',
    '0x4deb3edd991cfd2fcdaa6dcfe5f1743f6e7d16a6',
    '0x477573f212a7bdd5f7c12889bd1ad0aa44fb82aa',
    '0xce31190a03fc3c5f23167e88e75066824823222d',
    '0x60009b78da046ac64ef789c29ca05b79cdf73c10',
    '0x73c0ae50756c7921d1f32ada71b8e50c5de7ff9c',
    '0x60ae578abdfded1fb0555f54148fdd7b400a34ed',
    '0xa726c00cda1f60aaab19bc095d02a46556837f31',
    '0x0c0fe4e0236480e16b679ee1fd0c5247f9cf35f0',
    '0x0f4ee9631f4be0a63756515141281a3e2b293bbe',
    '0x97137466bc8018531795217f0ecc4ba24dcba5c1',
    '0x84d34f4f83a87596cd3fb6887cff8f17bf5a7b83',
    '0x78835265ac857bf3420830c71987b1a55f73c2dc',
    '0x4c8cfe078a5b989cea4b330197246ced82764c63',
    '0x073dca8acbc11ffb0b5ae7ef171e4c0b065ffa47',
    '0x3507e4978e0eb83315d20df86ca0b976c0e40ccb'
]


def print_db_data()
    for address in ALAMEDA:
        name = Wallet.name_at_address(ETHEREUM, address.lower())
        category = Wallet.category_at_address(ETHEREUM, address.lower())

        wallet_at_address = Wallet.at_address(ETHEREUM, address)
        console.print(address, '   ', wallet_at_address)


def get_alphabet_char_for_nth_wallet(n: int) -> str:
    result = divmod(n, 26)
    char = ALPHABET_UPPER[result[1]]
    return char * (result[0] + 1)

console.line(5)
for i, address in enumerate(ALAMEDA):
    print(f"{address.lower()},{ETHEREUM},Alameda Research {get_alphabet_char_for_nth_wallet(i)},fund,\"https://dune.com/queries/1542008\"")


FTX_BIG_RECIPIENTS = ['0xf1556137e7f45817e774096c5922f32c68ab15ae', '0xdb31651967684a40a05c4ab8ec56fc32f060998d', '0x554ccc18f88cf3159eedfe161cd46611ef820359','0x85464b207d7c1fce8da13d2f3d950c796e399a9c','0x95654afdaa3f10b8910a6a2eda210f1def629818','0x2e0122a3f4714bbadaa1ae5392b8759e41e815a3','0xd4621fbc86a3a2df239eacad9a3837155c617309','0x0eeb97a8fdcf2f70c5ebd97cab44a6cd3d8b3d60','0x2aee4201ee3e63040ef86e1fffe4e13e3faddca9','0x95808c0a3698117e0dbcaf1e717ca5d0b4c49fe7']
