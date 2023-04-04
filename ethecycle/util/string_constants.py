import re

ETHECYCLE = 'ethecyle'
DEBUG = 'DEBUG'

# Address stuff
ADDRESS = 'address'
FROM_ADDRESS = 'from_address'
MISSING_ADDRESS = 'no_address'
TO_ADDRESS = 'to_address'

# Chain stuff
BLOCKCHAIN = 'blockchain'
BLOCK_NUMBER = 'block_number'
CONTRACT = 'contract'
ERC20 = 'ERC20'
LOG_INDEX = 'log_index'
NFT = 'nft'
SYMBOL = 'symbol'
TOKEN_ADDRESS = 'token_address'
TOKEN = 'token'
TRANSACTION_HASH = 'transaction_hash'
TXN = 'transaction'
WALLET = 'wallet'

# Token symbols
USDT = 'USDT'
WETH = 'WETH'
TOKEN_REGEX = re.compile('^[A-Z]+$')

# Blockchains
ARBITRUM = 'arbitrum'
AVALANCHE = 'avalanche'
AVAX = 'avax'
BINANCE_SMART_CHAIN = 'bsc'
BITCOIN = 'bitcoin'
BITCOIN_CASH = 'bitcoin_cash'
CARDANO = 'cardano'
ETHEREUM = 'ethereum'
LITECOIN = 'litecoin'
MATIC = 'matic'
OASIS = 'oasis'
OKEX = 'okx_chain'
POLYGON = 'polygon'
RIPPLE = 'ripple'
SOLANA = 'solana'
TRON = 'tron'

# Txn properties in the graph
EXTRACTED_AT = 'extracted_at'
NUM_TOKENS = 'num_tokens'
ORGANIZATION = 'organization'
SCANNER_URL = 'scanner_url'

# Other column names
DATA_SOURCE = 'data_source'

# Industry
AAVE = 'aave'
ALAMEDA = 'alameda'
BINANCE = 'binance'
USDT = 'USDT'
USDT_ETHEREUM_ADDRESS = '0xdac17f958d2ee523a2206206994597c13d831ec7'

# Social Media
BITCOINTALK = 'bitcointalk'
DISCORD = 'discord'
FACEBOOK = 'facebook'
INSTAGRAM = 'instragram'
LINKEDIN = 'linkedin'
REDDIT = 'reddit'
TELEGRAM = 'telegram'
TIKTOK = 'tiktok'
TWITTER = 'twitter'
YOUTUBE = 'youtube'

# Order matters when choosing label cols from GoogleSheetsImporter: higher cols are chosen first
# For this reason we prefer more public orgs over less public ones.
SOCIAL_MEDIA_ORGS = [
    LINKEDIN,
    INSTAGRAM,
    TWITTER,
    YOUTUBE,
    REDDIT,
    TIKTOK,
    FACEBOOK,
    TELEGRAM,
    BITCOINTALK,
]

social_media_url = lambda org: f"{org}.org" if org == BITCOINTALK else f"{org}.com"
SOCIAL_MEDIA_URLS = [social_media_url(org) for org in SOCIAL_MEDIA_ORGS] + [
    'youtu.be'
]

# Wallet Categories
BRIDGE = 'bridge'
CATEGORY = 'category'
CEFI = 'cefi'
CEX = 'cex'
DAO = 'dao'
DEFI = 'defi'
DEX = 'dex'
EXCHANGE = 'exchange'
FTX = 'ftx'
HACKERS = 'hackers'
INDIVIDUAL = 'individual'
MIXER = 'mixer'
STABLECOIN = 'stablecoin'
VAULTS = 'vaults'
WALLET_PROVIDER = 'wallet provider'

# Misc
ALPHABET = 'abcdefghijklmnopqrstuvwxyz'
ALPHABET_UPPER = ALPHABET.upper()
HTTPS = 'https://'
JSON = 'json'
NAME = 'name'
WTF = '???'

# GraphML
LABEL_E = 'labelE'
LABEL_V = 'labelV'


