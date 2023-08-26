from ethecycle.models.address import Address

from ethecycle.util.string_constants import *
from ethecycle.blockchains.binance_smart_chain import BinanceSmartChain
from ethecycle.chain_addresses.address_db import drop_and_recreate_tables, get_db_connection

HECO = 'heco'
TABLES = ['wallets', 'tokens']

CHAIN_FIXES = {
    'avalanche': 'avax',
    'avalanche contract chain': 'avax-c',
    'bitcoin_cash': 'bch',
    'bnb_beacon': 'bnb',
}

TOKEN_RENAMES = [
    [Address(blockchain=BinanceSmartChain.SHORT_NAME, address='0x14016e85a25aeb13065688cafb43044c2ef86784'), 'BinancePeg-TUSD'],
    [Address(blockchain=BinanceSmartChain.SHORT_NAME, address='0x0e09fabb73bd3ade0a17ecc321fd13a19e81ce82'), CAKE],
    [Address(blockchain=HECO, address='0x0298c2b32eae4da002a15f36fdf7615bea3da047'), 'HecoPeg-HUSD'],
    [Address(blockchain=ETHEREUM, address='0xae78736cd615f374d3085123a210448e74fc6393'), rETH],
    [Address(blockchain=ETHEREUM, address='0xccf4429db6322d5c611ee964527d42e5d685dd6a'), cWBTC],
    [Address(blockchain=ETHEREUM, address='0x1a7e4e63778b4f12a199c062f3efdd288afcbce8'), agEUR],
    [Address(blockchain=ETHEREUM, address='0xE95A203B1a91a908F9B9CE46459d101078c2c3cb'), ankrETH],
    [Address(blockchain=ETHEREUM, address='0xbe9895146f7af43049ca1c1ae358b0541ea49704'), cbETH],
    [Address(blockchain=ETHEREUM, address='0x39ab32006afe65a0b4d6a9a89877c2c33ad19eb5'), 'cUSDT'],  # v1?
    [Address(blockchain=ETHEREUM, address='0xf650c3d88d12db855b8bf7d11be6c55a4e07dcc9'), 'cUSDT'],  # v2?
    [Address(blockchain=ETHEREUM, address='0x3231cb76718cdef2155fc47b5286d82e6eda273f'), EURe],
    [Address(blockchain=ETHEREUM, address='0x87611ca3403a3878dfef0da2a786e209abfc1eff'), eUSD],
    [Address(blockchain=ETHEREUM, address='0x514910771af9ca656af840dff83e8264ecf986ca'), 'LINK'],
    [Address(blockchain=ETHEREUM, address='0x8e870d67f660d95d5be530380d0ec0bd388289e1'), USDP],
    [Address(blockchain=ETHEREUM, address='0x7f39c581f595b53c5cb19bd0b3f8da6c935e2ca0'), wstETH],
    [Address(blockchain=ETHEREUM, address='0x1456688345527bE1f37E9e627DA0837D6f08C925'), 'Unit-USDP'],
    [Address(blockchain=POLYGON, address='0xe0b52e49357fd4daf2c15e02058dce6bc0057db4'), agEUR],
]


DECIMAL_CORRECTIONS = [
    [Address(blockchain=BinanceSmartChain.SHORT_NAME, address='0xa5ac8f8e90762380cce6c16aba17ed6d2cf75888'), 9],
    [Address(blockchain=HECO, address='0x0298c2b32eae4da002a15f36fdf7615bea3da047'), 8],
    [Address(blockchain=TRON, address='TR7NHqjeKQxGTCi8q8ZY4pL8otSzgjLj6t'), 6],
]

BURN_ADDRESSES = {chain: '0x0000000000000000000000000000000000000000' for chain in ['ethereum', 'bsc', 'heco']}
BURN_ADDRESSES['tron'] = 'T9yD14Nj9j7xAB4dbGeiX9h8unkKHxuWwb'


def import_token_corrections():
    conn = get_db_connection()

    def run_sql(sql):
        print(sql)
        conn.execute(sql)

    for token_rename in TOKEN_RENAMES:
        print(f"Setting {token_rename[0]} to {token_rename[1]}")

        sql = f"""
            UPDATE tokens SET name = '{token_rename[1]}'
            WHERE blockchain = '{token_rename[0].blockchain}'
            AND LOWER(address) = LOWER('{token_rename[0].address}')
        """

        run_sql(sql)

    for decimal_correction in DECIMAL_CORRECTIONS:
        print(f"Setting {decimal_correction[0]} to {decimal_correction[1]}")

        sql = f"""
            UPDATE tokens SET decimals = {decimal_correction[1]}
            WHERE blockchain = '{decimal_correction[0].blockchain}'
            AND LOWER(address)  = LOWER('{decimal_correction[0].address}')
        """

        run_sql(sql)

    # Fix chains and Aave org
    for t in TABLES:
        for old_chain, new_chain in CHAIN_FIXES.items():
            sql = f"""
                UPDATE {t}
                SET blockchain = '{new_chain}'
                WHERE blockchain = '{old_chain}'
            """
            run_sql(sql)

        # BNB chain
        sql = f"""
            UPDATE {t}
            SET blockchain = 'bnb'
            WHERE blockchain = 'bsc' AND LENGTH(address) <= 20 OR address LIKE 'bnb%'
        """
        run_sql(sql)

        # Aave
        sql=f"""
          UPDATE tokens
             SET organization = 'aave'
           WHERE name LIKE 'Aave%'
             AND symbol NOT LIKE 'AAVE'
             AND symbol <> 'Aave Token'
        """
        run_sql(sql)

    for blockchain, burn_address in BURN_ADDRESSES.items():
        sql=f"""
          UPDATE wallets
             SET name = 'NULL'
           WHERE blockchain = '{blockchain}'
             AND address = '{burn_address}'
        """
        run_sql(sql)
