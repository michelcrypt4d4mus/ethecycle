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


ALUSD  = 'ALUSD'
AMPL   = 'AMPL'
BEAN   = 'BEAN'
BUSD   = 'BUSD'
crvUSD = 'crvUSD'
DAI    = 'DAI'
DUSD   = 'DUSD'
ESD    = 'ESD'
EURST  = 'EURST'
eUSD   = 'eUSD'
FDUSD  = 'FDUSD'
FEI    = 'FEI'
FPI    = 'FPI'
FRAX   = 'FRAX'
GUSD   = 'GUSD'
HUSD   = 'HUSD'
LUSD   = 'LUSD'
PYUSD  = 'PYUSD'
R      = 'R'
sUSD   = 'sUSD'
stUSDT = 'stUSDT'
TUSD   = 'TUSD'
USDC   = 'USDC'
USDD   = 'USDD'
USDJ   = 'USDJ'
USDK   = 'USDK'
USDN   = 'USDN'
USDP   = 'USDP'
USDQ   = 'USDQ'
USDS   = 'USDS'
USDT   = 'USDT'


# Non-dollar stablecoins
agEUR = 'agEUR'   # Angle Protocol Euro
EUROC = 'EUROC'   # Circle Euro
EURe  = 'EURe'    # Monerium Euro
EURS  = 'EURS'
EURT  = 'EURT'    # Tether Euro
MXNT  = 'MXNT'    # Tether Mexican Peso
QC    = 'QC'
TAUD  = 'TAUD'    # TrueUSD AUD
TCAD  = 'TCAD'    # TrueUSD CAD
TCNH  = 'TCNH'    # TrueUSD CNH
TGBP  = 'TGBP'    # TrueUSD GBP
THKD  = 'THKD'    # TrueUSD HKD
XCHF  = 'XCHF'


# Gold stablecoins
DGLD  = 'DGLD'
DGX   = 'DGX'     # Digix Gold
PAXG  = 'PAXG'    # Paxos Gold
XAUT  = 'XAUT'    # Tether gold


### Other tokens that are not stablecoins
CAKE = 'CAKE'
CEL  = 'CEL'
LEO  = 'LEO'


# Wrapped tokens
cWBTC = 'cWBTC'
WBNB  = 'WBNB'
WBTC  = 'WBTC'
WETH  = 'WETH'
vBTC  = 'vBTC'
vBETH = 'vBETH'
vETH  = 'vETH'


# Staked tokens
aETH     = 'aETH'     # Aave ETH
ankrETH  = 'ankrETH'  # Ankr
BETH     = 'BETH'     # Binance Beacon ETH
cbETH    = 'cbETH'    # Coinbase
cETH     = 'cETH'     # Compound
frxETH   = 'frxETH'   # Frax ETH
LsETH    = 'LsETH'    # Liquid
rETH     = 'rETH'     # Rocket Pool
sfrxETH  = 'sfrxETH'  # FRAX
stETH    = 'stETH'    # LIDO
STETH    = 'STETH'    # Stakehound
wBETH    = 'wBETH'    # Wrapped Binance Beacon ETH
wstETH   = 'wstETH'   # Wrapped staked eth (LIDO?)
