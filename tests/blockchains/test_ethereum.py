from ethecycle.blockchains.ethereum import Ethereum


def test_known_wallets():
    assert Ethereum.wallet_label('0x6eff3372fa352b239bb24ff91b423a572347000d') == 'BIKI.com'


def test_token_address():
    assert Ethereum.token_address('USDT') == '0xdac17f958d2ee523a2206206994597c13d831ec7'


def test_token_decimals():
    usdt_address = Ethereum.token_address('USDT')
    assert Ethereum.token_decimals(usdt_address) == 6


def test_token_symbol():
    usdt_address = Ethereum.token_address('USDT')
    assert Ethereum.token_symbol(usdt_address) == 'USDT'
