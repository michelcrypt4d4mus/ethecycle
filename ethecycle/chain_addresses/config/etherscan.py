from typing import Optional

from ethecycle.util.list_helper import *
from ethecycle.util.string_constants import *


ETHERSCAN_LABEL_CATEGORIES = {
    BLOCKCHAIN: [
        'avalanche',
        'polygon-matic',
    ],
    BRIDGE: [
        'across-protocol',
        'bridge',
        'bridged-token',
        'wormhole',
    ],
    CEFI: [
        'blockfi',
        'celsius-network',
        'nexo',
    ],
    CEX: [
        'atomsolutions',
        'binance',
        'bitfinex',
        'bithumb',
        'bittrex',
        'coinbase',
        'crypto-com',
        EXCHANGE,
        'fiat-gateway',
        'ftx',
        'gemini',
        'hot-wallet',
        'huobi',
        'kraken',
        'kucoin',
        'marketplace',
        'okex',
        'otc',
        'resfinex',
        'upbit',  # TODO: ?
    ],
    CONTRACT: [
        'old-contract'
    ],
    DAO: [
        'bitdao',
        'chain',
        DAO,
        'dao-funds',
        'dxdao',
        'humanity',
        'mantra-dao',
        'olympusdao',
        'oracle-dao',
        'ooki',
        'redacted-cartel',
    ],
    'dapp': [
        'chainlink',
        'dappnode',
        'gnosis-safe',
        'instadapp',
        'loopring',
        'livepeer',
        'oobit',
        'pundi-x',
        'unstoppable-domains',
    ],
    DEFI: [
        '0x',
        '0x-ecosystem',
        '0xsplits',
        '0xuniverse',
        'aave',
        'arcx',
        'armor-fi',
        'augmented-finance',
        'aura-finance',
        'bancor',
        'bancor-contract-vulnerability',
        'compound',
        'compound-governance',
        'convex-finance',
        'cream-finance',
        'defi-education-fund',
        'defi-saver',
        'dydx',
        'enzyme-finance',
        'gearbox-protocol',
        'hakka-finance',
        'idle-finance',
        'inverse-finance',
        'juicebox',
        'kyber-network',
        'liquity',
        'lido',
        'maker',
        'maker-vault-owner',
        'nexus-mutual',
        'nuo-network',
        'polkastarter',
        'pooltogether',
        'rari-capital',
        'reserve-protocol',
        'reservelending',
        'revest-finance',
        'ribbon-finance',
        'rocket-pool',
        'saffron-finance',
        'set-protocol',
        'sorbet-finance',
        'staking',
        'synthetix',
        'unfederalreserve',
        'uniswap',
        'value-defi',
        VAULTS,
        'vesper-finance',
        'yam-finance',
        'yearn-finance',
        'yfii-finance',
        'yffi-finance',
        'ygov-finance',
        'yield-farming',
        'zapper-fi',
    ],
    DEX: [
        'airswap',
        'curve-fi',
        DEX,
        'keep2r',
        'mcdex',
        'shapeshift',
        'tokenlon',
    ],
    'funds': [
        'alchemist-coin',
        'bitcoin-suisse',
        'company-funds',
        'fund',
    ],
    'game': [
        'axie-infinity',
        'brave-frontier-heroes',
        'cryptosaga',
        'cryptospells',
        'decentraland',
        'dragonereum',
        'ether-cards',
        'etheremon',
        'gaming',
        'gods-unchained',
        'hyper-dragons',
        'megacryptopolis',
        'my-crypto-heroes',
        'raidparty',
    ],
    'gambling': [
        'gambling',
        'zethr',
    ],
    'gitcoin': [
        'gitcoin-grants',
    ],
    HACKERS: [
        'blocked',
        'compromised',
        'exploit',
        'heist',
        'high-risk',
        'parity-bug',
        'ponzi',
        'scam',
        'spam-token',
        'take-action',
    ],
    'individual': [
        'airdrop-hunter',
        'grantee',
        'snapshot-voter',
        'gitcoin-grantee',
        'top-degen',
        'writer',
    ],
    'layer-2': [
        'arbitrum',
        'layer-2',
        'metis-andromeda',
    ],
    'market maker': [
        'fortube',
        'nest-protocol',
        'premia',
        'saddle-finance',
        'sudoswap',
        'sushiswap',
        'swipeswap',
    ],
    'mev': [
        'mev-bot',
        'opportunist',
    ],
    MIXER: [
        'tornado-cash',
        'typhoon-cash',
    ],
    'multisig': [
        'multisig-owner',
    ],
    NFT: [
        'art-blocks',
        'blockchain-cuties',
        'collectibles',
        'cryptopunks',
        'cryptokitties',
        'gem',
        'looksrare',
        'metamask',
        'neo-tokyo',
        NFT,
        'opensea',
        'rarible',
        'solv-protocol',
        'stoner-cats',
        'superrare',
    ],
    'payments': [
        'payments',
        'ren',
        'swipe-io',
        'unibright',
    ],
    STABLECOIN: [
        'abracadabra-money',
        'fei-protocol',
        'hop-protocol',
        'mstable',
        'reflexer-finance',
        STABLECOIN,
        'trusttoken',
        'unit-protocol',
        'usdc',
    ],
    TOKEN: [
        'medikey',
        'meettoken',
    ],
    WALLET_PROVIDER: [
        'authereum',
        'bitpie',
        'wallet-app',
        'zerion',
    ]
}

# Presence of one of these labels means the category is that label
DETERMINATIVE_LABELS = [
    'balancer',
    'burn',
    'contract-deployer',
    'donate',
    'ens',
    'factory-contract',
    'mining',
    'multichain',
    'sybil-delegate',
    'token-sale',
]


def determine_category(labels: List[str]) -> Optional[str]:
    for category, category_labels in ETHERSCAN_LABEL_CATEGORIES.items():
        if has_intersection(labels, category_labels):
            return category

    if any(label.endswith('-hack') or label.endswith('-scam') for label in labels):
        return HACKERS
    elif len(intersection(DETERMINATIVE_LABELS, labels)) > 0:
        return intersection(DETERMINATIVE_LABELS, labels)[0]
    elif 'balancer-vested-shareholders' in labels:
        return 'balancer'
    elif 'ico-wallets' in labels:
        return 'ico'
    elif 'wbtc-merchant' in labels or 'wrapped-bitcoin' in labels:
        return 'wbtc'
    else:
        return None
