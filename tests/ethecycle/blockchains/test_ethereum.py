from ethecycle.blockchains.ethereum import Ethereum


def test_wallet_labels():
    assert Ethereum.wallet_label('0x6eff3372fa352b239bb24ff91b423a572347000d') == 'BIKI 1'
