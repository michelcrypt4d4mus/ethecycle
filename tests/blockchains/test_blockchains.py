
from ethecycle.models.blockchain import guess_chain_info_from_address
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.blockchains.bitcoin import Bitcoin
from ethecycle.blockchains.tron import Tron


def test_guess_chain_info_from_address():
    assert guess_chain_info_from_address('0x3d4E3413babB4cd2ef5220e2cD64e64439B3514E') == Ethereum
    assert guess_chain_info_from_address('3DcTzg5Gyaj7JSAQu7gkqsoMztzUfwgT4u') == Bitcoin
    assert guess_chain_info_from_address('T9zs7iRBoPzUFEjiDVwyghsoEnnzqbtrq2') == Tron
