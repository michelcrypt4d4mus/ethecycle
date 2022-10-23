from ethecycle.util.dict_helper import get_dict_key_by_value

ADDRESS = 'address'
NUM_TOKENS = 'num_tokens'
TXN = 'transaction'
WALLET = 'wallet'

USDT = 'USDT'
WETH = 'WETH'

LABEL_E = 'labelE'
LABEL_V = 'labelV'

TOKENS = {
    USDT: '0xdac17f958d2ee523a2206206994597c13d831ec7'.lower(),
    WETH: '0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2'.lower(),
    'PILLAGERS': '0x17f2fdd7e1dae1368d1fc80116310f54f40f30a9'.lower(),
}


def get_token_by_address(token_address: str) -> str:
    try:
        return get_dict_key_by_value(TOKENS, token_address)
    except ValueError:
        return 'unknown'
