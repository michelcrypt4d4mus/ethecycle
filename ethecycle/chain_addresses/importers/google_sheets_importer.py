"""
Read public sheets: https://medium.com/geekculture/2-easy-ways-to-read-google-sheets-data-using-python-9e7ef366c775#e4bb
A copy of each sheet will be written to the repo so that we still have the data should
the sheet disappear because the Google account was canceled or similar.
"""
import re
from dataclasses import dataclass, field
from os import path

import numpy as np
import pandas as pd
from rich.panel import Panel
from rich.pretty import pprint
from typing import List, Optional, Type
from urllib.parse import urlencode

from ethecycle.blockchains.arbitrum import Arbitrum
from ethecycle.blockchains.binance_smart_chain import BinanceSmartChain
from ethecycle.blockchains.bitcoin import Bitcoin
from ethecycle.blockchains.chain_info import ChainInfo
from ethecycle.blockchains.core import Core
from ethecycle.blockchains.ethereum import Ethereum
from ethecycle.blockchains.fantom import Fantom
from ethecycle.blockchains.polygon import Polygon
from ethecycle.blockchains.ronin import Ronin
from ethecycle.chain_addresses.address_db import insert_addresses
from ethecycle.config import Config
from ethecycle.models.wallet import Wallet
from ethecycle.util.filesystem_helper import RAW_DATA_DIR
from ethecycle.util.logging import console, log, print_indented
from ethecycle.util.number_helper import pct, pct_str
from ethecycle.util.string_constants import (ADDRESS, BITCOINTALK, FACEBOOK, HTTPS, INDIVIDUAL,
     SOCIAL_MEDIA_ORGS, SOCIAL_MEDIA_URLS, WALLET, social_media_url)
from ethecycle.util.string_helper import has_as_substring

# Keys are spreadsheet IDs, values are worksheet IDs in that spreadsheet
ETHEREUM_SHEETS = {
    '1I30YwfcqO7r7hP63hKdJM1BaaqAWiFfz_biIk2fyouM': [
        'Form Responses 1'
    ],
    '1ou1tDAiQ18Y9stKtl7DiiMe6ARlLxPhtFb3pXgVEEYI': [
        'Twitter Campaign',
        'Facebook',
    ],
    '1wVkp__Rw8OaOsavxCeUOP5ViE9y0-iywnAuYsPk714E': [
        'LinkedIn Bounty',
        'Reddit Bounty',
        'Telegram Airdrop',
        'Blog and Media Bounty',
        'Signature Bounty',
        'Twitter Bounty',
        'Facebook Bounty',
    ],
    '1lRkldOzXR5s1kBvbSN8tW_ux5H6ob9YaTW4EP3CkRhU': [
        'TWITTER',
        'FACEBOOK',
        'LINKEDIN',
        2141942915,
        'YOUTUBE',
        'Translation'
    ],
    '1eSfJWCthTyeL_1n6SK8s8SFF3ULA1XG2FBAa-PsVuP0': [
        'Telegram',
        'YouTube',
        'Reddit',
        'Facebook',
        'Translations',
        'Twitter',
    ],
    '1YJq5IAIrjavjNIMQLw7SeVx2_bydwdXELHLxnJhYfSk': [
        'Form Responses 1'
    ],
    '1eZ0gF5Qq6UnEs2hWPIvgE-L9J4uONz134sxnW-T6iBE': [
        'Report Week 1',
        'Content Campaign',
        'Youtube',
        'Twitter',
        'Telegram',
        'Linkedin',
        'Voting Campaign'
    ],
    '1RWH_9vWn3hqnWPST-H5jwSljUneR5xG-yVLu3R9gSGs': [
        'Sign up Bounty',
        'Ramadan Bounty',
        'Form Responses 16',
        'Bittrex Listing Bounty',
        'Poloniex Listing Bounty',
        'Okex Listing Bounty',
        'Huobi Listing Bounty',
        'Binance Listing Campaign',
        '6th AMA',
        'Rejected',
        '3rd AMA Bounty',
        '1st AMA Bounty',
        'Telegram Invitation',
        'CMC Listing Campaign'
    ],
    '1nFL75ojBWi0dNQjX6UcKh8WdvGXYmP23lHiSZdfv8f4': [
        'Sheet1'
    ],
    '1_Ozxkj3WitAiwocvD_o-tscCwT5o_Wn9mAcbv_qcBkQ': [
        'Social Media Campaign',
        'Reddit Campaign',
        'Signature Campaign',
        191343910,
    ],
    '1KX42FnK2TAZ2caf14TiJ5LbA7rUnsHIHX-FdJPfqx5k': [
        'Form Responses 1'
    ],
    '1gFGizvgADXVHMNhiP0WlFJY2floPpIaU14OecgngDXo': [
        'Twitter Campaign',
    ],
    '1VN61OS92gyZSHlYorDMfVVf90n3jl-HKTGbhBXVthNE': [
        'Final sheet Signature',
        'Final Translation',
        'Twitter Bounty',
        'Facebook Bounty',
        'Translation Bounty',
        'Blog/Media Bounty',
        'Signature',
    ],
    '1VY4YK06p_9Mn0tPlHoXO_N3KJZbwGB18uypXSQtk3Gc': [
        'Twitter Master Sheet',
        'Facebook Master Sheet',
        'Telegram Groups',
        'Signature',
    ],
    # This one has 282K rows!
    '1SamWX8hjMLuMx7B03S4QTR6V_dCCkcXN5PBJJdLKjnw': [
        'Form Responses 1',
    ],
    '1WCVpua051XBlLfIZpKrcQMmx_JT2JujtyJIX-bU5o5w': [
        'Application Signature Campaign',
        'Application Translation',
    ],
    '1QlbETkBQAgnSJth5Na2ypQL-RaE_b1tddBX1rqT5ZK8': [
        'Twitter Bounty',
        'Facebook Bounty',
        'Blog/Media-Final Sheet',
        'Blog and Media',
        'Signature Campaign',
        'Translations',
    ],
    '1oF6vA71id2xDp8GTxY7xBMNz67ZpbwVDAzhDeIXtnzo': [
        1187103448,
        'Twitter',
        'Facebook',
        'Instagram',
        'Youtube',
        'LinkedIn',
        'Translation'
    ],
    '1JljucXr5mJU1m2rA63NgRa7pwvmRtkIjjYHPVGpolZA': [
        'Facebook',
        'Twitter',
        'YouTube',
        'Media',
        'VK',
    ],
}

BITCOIN_SHEETS = {
    '15MyV7FiYq2cqTSqTYnObrmhD29VxmzxPrckoR6XV1qA': [
        'Signature Campaign',
        'Twitter Bounty',
        'Facebook Bounty',
        'Blog/Media',
    ],
}

# Some sheets have no address column
# TODO: reconfigure these as AirdropGoogleSheets
DEFAULT_LABELS = {
    '1nFL75ojBWi0dNQjX6UcKh8WdvGXYmP23lHiSZdfv8f4': 'petscoin recipient',
    '1YJq5IAIrjavjNIMQLw7SeVx2_bydwdXELHLxnJhYfSk': 'crykart recipient',
}

SHEETS_ARGS = {'tqx': 'out:csv'}
CHARS_THAT_NEED_QUOTE = [c for c in '):;"|-_*&']
ETHEREUM_ADDRESS_REGEX = re.compile('(eth(ereum)?|erc-?20)\\s+(wallet|address)', re.IGNORECASE)
WALLET_ADDRESS_REGEX = re.compile('^wallet\\s+.*\\s*address', re.IGNORECASE)
SHEETS_URL = 'https://docs.google.com/spreadsheets/d/'
VALID_ADDRESS = 'valid_address'

# Fix the embedded timestamp so that every write of a gzipped CSV doesn't change the binary
GZIP_COMPRESSION_ARGS = {'method': 'gzip', 'mtime': 1667767780.0}
GZIPPED_CSV_DIR = str(RAW_DATA_DIR.joinpath('google_sheets'))

# Min % of col matching a URL or @something style string
SOCIAL_MEDIA_PCT_CUTOFF = 88.0

# Max # of mismatches if there are > 1 possible address cols
MAX_MISMATCHES = 10


# Theoretically this dataclass allows better configurability, use it going forward
@dataclass
class AirdropGoogleSheet:
    airdrop_name: str
    sheet_id: str
    chain_info: Type[ChainInfo]
    use_default_labels: bool = True  # Means the title will be used
    worksheet_names: Optional[List[str]] = None
    column_letter: Optional[str] = None
    social_media_link: Optional[str] = None
    address_column: Optional[str] = None
    category: str = 'airdrop'
    force_extract_labels: bool = False
    is_airdrop: bool = True  # TODO: make this actually do something (not append "Airdrop" to label)

    def __post_init__(self):
        self.worksheet_names = self.worksheet_names or ['Sheet1']

        if not isinstance(self.worksheet_names, list):
            raise ValueError(f"'{self.worksheet_names}' is not a list it's a {type(self.worksheet_names)}")


# This is the way sheets should be configured going forward
AIRDROP_SHEETS = [
    AirdropGoogleSheet(
        airdrop_name='PhoenixDefi $PNIX',
        sheet_id='1XbLd80BaH8svKeJlJWdJvfxpvN2epxhMnYNBl2LHUKU',
        social_media_link='https://twitter.com/phoenixdefi/status/1377274242497196034',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Isekai Battle Ticket',
        sheet_id='1WbBUGZqryUIzh_o8kW-GKk5CksAvYfGox_ZRexQJVY4',
        worksheet_names=['csv'],
        social_media_link='https://twitter.com/Isekai_Battle/status/1624010711210037248',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='@gillesdc Magritte Checks',
        sheet_id='1FKbl_3mlzEihBQltve3nJY9rMSpC-uVZdlKlFLOmokw',
        worksheet_names=[
            'Phase 1+2 - Allowlist Verification Of Man',
            'Phase 1+2 - Allowlist Heymint',
            'Phase 2 - Waitlist'
        ],
        social_media_link='https://twitter.com/gillesdc/status/1633870540409827329',
        chain_info=Ethereum,
        is_airdrop=False
    ),
    AirdropGoogleSheet(
        airdrop_name='Lido LDO Token',
        sheet_id='10gvpGZKhoIBmGqUOUJAhuqdeR0xhFmmqNpRUKLIRaxU',
        worksheet_names=['FRAMEWORK'],
        social_media_link='https://twitter.com/tumilett/status/1621533934197637127',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='PandAI DEX Competition',
        sheet_id='1Sdcp6jghR73KCbvdMKsZNi8DlKmUiQAbd0glJMjCk5E',
        worksheet_names=['Results'],
        social_media_link='https://twitter.com/pandai_bsc/status/1636361641695793152',
        chain_info=BinanceSmartChain
    ),
    AirdropGoogleSheet(
        airdrop_name='Clover Finance CLV & Galxe',
        sheet_id='1-1ag1I6UhHqWBCS_qm5ucnt92MrUrL3dtueb1MEm8bk',
        social_media_link='https://twitter.com/clover_finance/status/1574402545912795137',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Clover Finance CLV & Galxe',
        sheet_id='1-GlKye58eofVAF5JI0vFM_o4jghNMq9qSkUN73Lt1oI',
        social_media_link='https://twitter.com/clover_finance/status/1574402545912795137',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Equalizer Exchange DEX',
        sheet_id='1KkY6sb7Bx7kUitiVw6E4bdCrzsqloTjUYlSJcSpbJMs',
        worksheet_names=['List'],
        address_column='0xcba1a275e2d858ecffaf7a87f606f74b719a8a93', # Hack bc there is no header
        social_media_link='https://twitter.com/Equalizer0x/status/1597696867533398016',
        chain_info=Fantom
    ),
    AirdropGoogleSheet(
        airdrop_name='League Of Empires - Super',
        sheet_id='1gBS5GhYg_eC1G2I86_Eh4YbgDTKmvGzN4N9aL-WU7C4',
        address_column='0xD37b6461e729fB88C960dc2bC37B9672fF5dD7d9', # Hack bc there is no header
        worksheet_names=['Random 1000 member: 30 $LOE'],
        social_media_link='https://twitter.com/LeagueofEmpires/status/1511900715635003393',
        chain_info=Polygon
    ),
    AirdropGoogleSheet(
        airdrop_name='PolkaBridge INO',
        sheet_id='1WkmOcm1Q7ebACeuNKsnEs6fLeQfyOmfid_oDonnIZt4',
        social_media_link='https://twitter.com/realpolkabridge/status/1510624657593942020',
        chain_info=Polygon
    ),
    AirdropGoogleSheet(
        airdrop_name='Oceans of Terra',
        sheet_id='127_TQJ3yL7dsvTVj92dcMENj1YGhG79XTA288W7R4c0',
        social_media_link='https://twitter.com/OceansOfTerra/status/1647071846892965893',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Infinity Node',
        sheet_id='1slo3BJuByq0IFOOrchj3Qb82e4ayySBLZvmaMfDKLC4',
        worksheet_names=['Valid addresses'],
        social_media_link='https://twitter.com/_InfinityNode/status/1649794391127769088',
        chain_info=Ronin,
        address_column='23/04/2022'
    ),
    AirdropGoogleSheet(
        airdrop_name='PoolPhiesta - Pfers Giveaway (Pooly)',
        sheet_id='1L9vBE3GT8_CSa08rpYlyIxA-TBNq5V61nvukvqs_XFc',
        worksheet_names=['Last 30 days'],
        social_media_link='https://twitter.com/phi_xyz/status/1647882436481777664',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='CoreDoge',
        sheet_id='1B4T-OfP3NBOHaNnfK7WJJMFaoDXGCbBzRtm08vE1gR4',
        worksheet_names=['Whitelist for Pre-Sale'],
        social_media_link='https://twitter.com/CoreDoge_xyz/status/1648735050501062658',
        chain_info=Core
    ),
    AirdropGoogleSheet(
        airdrop_name='MEEET-MAMA NFT',
        sheet_id='1uwfwNDNMqeZ8n82JvtPvcvFb6x93ljlSyemk_kNG6N4',
        social_media_link='https://twitter.com/MEEETOfficial/status/1645348134149664768',
        chain_info=Arbitrum
    ),
    AirdropGoogleSheet(
        airdrop_name='WOO Ventures',
        sheet_id='14cbpXi6qNK3eLuzf5m889PJdIQS2l6QU2VbWybNrm-k',
        worksheet_names=[f"{t} winners" for t in 'QRDO ERP LUNR STRP DERI CLH'.split(' ')],
        social_media_link='https://twitter.com/_WOO_X/status/1629138526745796608',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Smurfs Society',
        sheet_id='1mknqz_Eyos3MfNoZzK-IFQ9b63DzhMGt_k4McdTvuBM',
        social_media_link='https://twitter.com/phaverapp/status/1625365316904849409',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='0xdgb Here For The Memes NFT',
        sheet_id='1Jyt6VGuO_fbJol2B2EhQX4UZ1Tdm-dPB9qTfU-SXylQ',
        worksheet_names=['Edition Raffle - Feb 8th', '0xdgb CA'],
        social_media_link='https://twitter.com/0xdgb/status/1632833434346217477',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Buffer Finance incident compensation',
        sheet_id='1H9-2-QWhJKPzkKNqPHGCirI8gXjiEPm4OZ6HkdFxm-U',
        worksheet_names=['USDC', 'ARB', 'Airdrop Master'],
        social_media_link='https://twitter.com/Buffer_Finance/status/1649117988623089680',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Yubiwa (OG) NFT',
        sheet_id='1odK0HrNSvSFjojnQYPGBXdjWlaacBGf0FuIqdcPRsmc',
        social_media_link='https://twitter.com/BishojoClub/status/1640619473161060353',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='DexMart Wallet x Meta Galaxy',
        sheet_id='1ZcKf4GXMDaf7pT1I_BpQQMWKbArUCeoLP1jwlLj5wWM',
        social_media_link='https://twitter.com/Meta_Galaxyy/status/1648688991171137536',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Punkzi',
        sheet_id='1iVEzrjMxdasUiwJUuChSsspyz-8YR09U6sJiFihsM2E',
        social_media_link='https://twitter.com/Punkzi_NFT/status/1623413002568364032',
        worksheet_names=['Ark1'],
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='@ozark.eth MemesFTP',
        sheet_id='1-QUJdfrsipsPU4xQ29MzWihIlNhUlHjcm6uPKYrZHf0',
        social_media_link='https://twitter.com/OzarkNFT/status/1620522573569343489',
        worksheet_names=['SINK', '3-14-23-Snapshot'],
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='(B)APETAVERSE TEE shirt',
        sheet_id='1BGKng4fPnk79pLmwwZJbUVfKzPN7Qe6P',
        social_media_link='https://twitter.com/bapetaverse/status/1518051405525037056',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Telegram Venue Winners - 100BNB',
        sheet_id='1G1BO1TSzet-CZ-W4lrUDdxzf8b_vlnLH5QYhXBdO2-4',
        social_media_link='https://twitter.com/Assure_pro/status/1514242008331665410',
        chain_info=BinanceSmartChain
    ),
    AirdropGoogleSheet(
        airdrop_name='UBOXSEA X STONE AEON',
        sheet_id='1Bo_xxklIlWE33QD9hkDM5zAzWDbr-Yn9E77weASsODE',
        social_media_link='https://twitter.com/UBOXDAO/status/1516344457557204992',
        worksheet_names=['Winner list'],
        chain_info=Ethereum,
        force_extract_labels=True
    ),
    AirdropGoogleSheet(
        airdrop_name='PlayerDAO Meta 4MW 4th Round',
        sheet_id='1BLsLQRWRMD4cZqNsziBUWLC0vScZH3VUJXEFMEcT2Eg',
        social_media_link='https://twitter.com/4metas/status/1516010240776581120',
        chain_info=BinanceSmartChain
    ),
    AirdropGoogleSheet(
        airdrop_name='Inu Base INUB',
        sheet_id='1SsVdgERDFUWHoyjOw0WTw1uweWK5Bedzb8JAH7YZVc0',
        social_media_link='https://twitter.com/InuBase/status/1517550013429166080',
        chain_info=BinanceSmartChain
    ),
    AirdropGoogleSheet(
        airdrop_name='@xHashtagio x @CropBytes CBX Token',
        sheet_id='1ceff5md1U-RrdeHP-jMW4wUe-twqxg7ELBpoiEnDow4',
        social_media_link='https://twitter.com/InuBase/status/1517550013429166080',
        chain_info=Ethereum
    ),
    AirdropGoogleSheet(
        airdrop_name='Simeta 4th',
        sheet_id='1rC89Axrhen3v_opVQth-75dYghlVo28dkQHOIeDyqUU',
        social_media_link='https://twitter.com/simeta_io/status/1517388285458280448',
        chain_info=BinanceSmartChain,
        force_extract_labels=True
    ),
    AirdropGoogleSheet(
        airdrop_name='Zonoswap x HyperPay',
        sheet_id='1i3WKWTLK9Re-OSKtMV5fjfmos-svH9eC',
        worksheet_names=['Worksheet'],
        social_media_link='https://twitter.com/ZonoSwap/status/1516048628275900416',
        chain_info=BinanceSmartChain,
        force_extract_labels=True
    ),
    AirdropGoogleSheet(
        airdrop_name='@Youcoin $UCON',
        sheet_id='1X8932D6f9wbuQi5qEJT7QPVP6RCOH4DdOCiUQTUxuOQ',
        social_media_link='https://twitter.com/YouCoinOnline/status/1516331019959365633',
        chain_info=BinanceSmartChain
    ),
]

# Possible others:
#  * Meebits? https://docs.google.com/spreadsheets/d/1BNgfiIDql0SExFbthyvUhVc0MSj2IQqOzBeU6bN4MXM/edit#gid=0
#  * published so not a sheet as is: '2PACX-1vS_UEpiHM5HW-_cc9UgMx1FaBqkVFOspoDxxXNm2sKPAWnb2jh0iy1WDuKaZARP_xGgozuXL9G2VP93'
#  * Some Ripple tokens and addresses: https://docs.google.com/spreadsheets/d/1kIjUN-jJzDxciMedJZo2XPyL-VQ-Zs1zt0YCgy6Cmcc/edit#gid=0
#  * Arbitrum: https://twitter.com/lucianlampdefi/status/1631702362351112194
#  * Tezos: https://docs.google.com/spreadsheets/d/1Y7q8dWpIyWX6GnRNW2_nqr_vF7TBTplq/edit#gid=1892551471
#  * PokeMine
    # Can't be loaded because double wide header column
    # AirdropGoogleSheet(
    #     airdrop_name='PokeMine & Coinhub',
    #     sheet_id='12QSLF_9TLCVug_35OYYYcMIoC6UpR8_aUYbxUug4U70',
    #     worksheet_names=['PokeMine & Coinhub - List of Winners'],
    #     address_column='Top 5 invitees ',
    #     social_media_link='https://twitter.com/PokeMineGo/status/1515915853757583362',
    #     chain_info=BinanceSmartChain,
    # ),

def import_google_sheets() -> None:
    for sheet_id, worksheets in ETHEREUM_SHEETS.items():
        for worksheet_name in worksheets:
            worksheet = GoogleWorksheet(sheet_id, worksheet_name, Ethereum)
            insert_addresses(worksheet.extract_wallets())
            console.line(2)

    for sheet_id, worksheets in BITCOIN_SHEETS.items():
        for worksheet_name in worksheets:
            worksheet = GoogleWorksheet(sheet_id, worksheet_name, Bitcoin)
            insert_addresses(worksheet.extract_wallets())
            console.line(2)

    # This is the way sheets should be configured going forward
    for airdrop_sheet in AIRDROP_SHEETS:
        for worksheet_name in airdrop_sheet.worksheet_names:
            worksheet = GoogleWorksheet(
                sheet_id=airdrop_sheet.sheet_id,
                worksheet_name=worksheet_name,
                chain_info=airdrop_sheet.chain_info,
                default_label_base=airdrop_sheet.airdrop_name + ' airdrop recipient',
                address_column=airdrop_sheet.address_column,
                category=airdrop_sheet.category,
                force_extract_labels=airdrop_sheet.force_extract_labels
            )

            insert_addresses(worksheet.extract_wallets())
            console.line(2)


class GoogleWorksheet:
    def __init__(
            self,
            sheet_id: str,
            worksheet_name: str,
            chain_info: Type[ChainInfo],
            default_label_base: Optional[str] = None,
            address_column: Optional[str] = None,
            category: Optional[str] = None,
            force_extract_labels: bool = False
        ) -> None:
        """
        If provided:
          * 'default_label_base' is used as the wallet label / name
          * 'address_column' specifies where to find addresses
          * 'force_extract_labels' means look for social medai cols, don't just use 'default_label_base'
        """
        self.sheet_id = sheet_id
        self.worksheet_name = worksheet_name
        self.chain_info = chain_info or Ethereum
        self.default_label_base = default_label_base
        self.address_column = address_column
        self.category = category
        self.force_extract_labels = force_extract_labels
        self.mismatch_count = 0
        self._build_url()
        self.df = pd.read_csv(self.url)
        self.df = self.df[[c for c in self.df if not c.startswith("Unnamed")]]
        self.df_length = len(self.df)
        self.column_names = list(self.df.columns.values)
        self.email_col = None
        self._write_df_to_csv()

    def extract_wallets(self) -> List[Wallet]:
        self.address_col_label = self.address_column or self._guess_address_column()
        print_indented(f"Wallet column: '{self.address_col_label}'")

        # Remove rows with null addresses
        self.df = self.df[self.df[self.address_col_label].notnull()]
        non_null_address_count = len(self.df)
        self.null_address_count = self.df_length - non_null_address_count

        # Determine which social media column is suitable for use as the wallet label
        self.social_media_col_label = self._guess_social_media_column()
        self.df[self.social_media_col_label].str.strip()

        # Strip whitespace from remaining rows' addresses and check filter invalid rows
        self.df[self.address_col_label].str.strip()
        is_valid_address = lambda r: self.chain_info.is_valid_address(r[self.address_col_label])
        self.df[VALID_ADDRESS] = self.df.apply(is_valid_address, axis=1)
        valid_address_df = self.df[self.df[VALID_ADDRESS] == True]
        self.invalid_address_count = non_null_address_count - len(valid_address_df)

        # Build Wallet() objects for valid rows
        wallets = [self._build_wallet(row) for (_row_number, row) in valid_address_df.iterrows()]
        self._print_extraction_stats()

        if Config.debug:
            for wallet in wallets[0:10]:
                pprint(wallet)

        return wallets

    def _build_wallet(self, df_row: pd.Series) -> Wallet:
        row = df_row.to_dict()
        address = row[self.address_col_label]
        wallet_name = row[self.social_media_col_label]

        if isinstance(wallet_name, float) and np.isnan(wallet_name):
            name = '?'
        else:
            name = row[self.social_media_col_label].removeprefix(HTTPS).removeprefix('www.')

            if has_as_substring(name, SOCIAL_MEDIA_URLS) and '?' in name:
                name = name.split('?')[0].strip()

        wallet = Wallet(
            address=address,
            chain_info=self.chain_info,
            category=INDIVIDUAL,
            data_source=self.url,
            name=name
        )

        return wallet

    def _build_url(self):
        """Build google sheets URL."""
        base_url = f"{SHEETS_URL}{self.sheet_id}"

        if isinstance(self.worksheet_name, int):
            self.url = f"{base_url}/export?format=csv&gid={self.worksheet_name}"
        else:
            args = SHEETS_ARGS.copy()
            args['sheet'] = self.worksheet_name
            self.url = f'{base_url}/gviz/tq?{urlencode(args).replace("/", "%%2F")}'

        console.print(f"Reading sheet '{self.worksheet_name}' from '{self.url}'...")

    def _guess_address_column(self) -> str:
        """Guess which col has the addresses."""
        wallet_cols = [c for c in self.column_names if ETHEREUM_ADDRESS_REGEX.search(c)]

        # Do a 2nd pass to look for more generic labels
        if len(wallet_cols) == 0:
            wallet_cols = [c for c in self.column_names if WALLET_ADDRESS_REGEX.search(c)]

        # 3rd pass to look for cols titled 'address'
        if len(wallet_cols) == 0:
            wallet_cols = [
                c for c in self.column_names
                if any(word in c.lower() for word in [ADDRESS, 'receiver', WALLET, 'your name']) and 'token' not in c.lower()
            ]

        if len(wallet_cols) == 0 and len(self.column_names) == 1:
            wallet_cols = self.column_names

        if len(wallet_cols) == 0:
            raise ValueError(f"No address columns found in {self.column_names}")
        elif len(wallet_cols) == 1:
            return wallet_cols[0]
        elif len(wallet_cols) > 2:
            raise ValueError(f"{len(wallet_cols)} wallet columns found in {self.column_names}")

        print_indented(f"Checking possible wallet cols: {wallet_cols}", style='possibility')
        wallet_cols_df = self.df[wallet_cols]

        mismatches = wallet_cols_df[
               (wallet_cols_df[wallet_cols[0]] != wallet_cols_df[wallet_cols[-1]])
            & ~(wallet_cols_df[wallet_cols[0]].isna() & wallet_cols_df[wallet_cols[0]].isna())
        ]

        def count_valid_rows(col):
            is_valid_address = lambda row: self.chain_info.is_valid_address(row[col])
            return len(self.df[self.df.apply(is_valid_address, axis=1)])

        valid_row_counts = {col: count_valid_rows(col) for col in wallet_cols}
        console.print(f"Valid Row Counts: {valid_row_counts}")

        # Hack to handle cases where one col is an actual address column and the other is not an address col.
        if 0 in valid_row_counts.values():
            self.mismatch_count = 0

            for col, valid_row_count in valid_row_counts.items():
                if valid_row_count > 0:
                    return col

        self.mismatch_count = len(mismatches)

        if self.mismatch_count <= MAX_MISMATCHES:
            return wallet_cols[0]
        else:
            console.print(Panel(f"Mismatches between possible wallet address cols:"))
            print(mismatches)
            raise ValueError(f"Too many mismatches ({self.mismatch_count} > {MAX_MISMATCHES})")

    def _guess_social_media_column(self) -> str:
        """
        Guess which col has addresses (or place the configured DEFAULT_LABELS value in 'facebook' col).
        Or check self.default_label_base in which case use labels based on that
        """
        if self.sheet_id in DEFAULT_LABELS or (self.default_label_base is not None and not self.force_extract_labels):
            label = self.default_label_base or DEFAULT_LABELS[self.sheet_id]
            print_indented(f"Applying default label '{label}'...")
            self.df[FACEBOOK] = self.df.apply(lambda row: f"{label} {row.name}", axis=1)
            self.column_names = self.df.columns.values
            return FACEBOOK

        social_media_cols = [
            c for c in self.column_names
            if any(social_media_org in c.lower() for social_media_org in SOCIAL_MEDIA_ORGS) \
                or c.lower() in ['name', 'your name']
        ]

        social_media_cols = sorted(
            social_media_cols,
            key=lambda c: "zz_{c}" if (BITCOINTALK in c.lower() or ' post ' in c.lower()) else c
        )

        print_indented(f"All column names: {self.column_names}", style='color(130) dim')
        print_indented(f"Checking possible social media columns: {social_media_cols}", style='possibility')

        # First check social media cols then fall back to 'email' and 'profile' or similar
        for col in social_media_cols:
            if self._is_good_label_col(col):
                return col

        for col in self.column_names:
            if col in social_media_cols:
                continue

            if self._is_good_label_col(col):
                return col

        if self.email_col:
            return self.email_col

        raise ValueError(f"No social media column identified!")

    def _is_good_label_col(self, col: str) -> bool:
        """True if we should use this column as the wallet label based on col name and values."""
        if not isinstance(col, str):
            log.debug(f"Column '{col}' is not a string, skipping...")
            return False

        col_lowercase = col.lower()
        social_media_org = next((org for org in SOCIAL_MEDIA_ORGS if org in col_lowercase), None)

        if social_media_org:
            substring = social_media_url(social_media_org)
        elif col_lowercase.startswith('profile') or col_lowercase.startswith('vk '):
            substring = HTTPS
        elif 'email' in col_lowercase:
            log.info(f"Found email col: {col}")
            self.email_col = col
            return False
        elif 'name' in col_lowercase:
            # This allows any string
            substring = ''
        else:
            return False

        log.debug(f"    Substring to look for '{col}' profile is '@' prefix or '{substring}'...")
        row_count = len([c for c in self.df[col] if isinstance(c, str) and (substring in c or c.startswith('@'))])
        msg = f"'{col}': {row_count} of {self.df_length} ({pct_str(row_count, len(self.df))} good label)"

        if pct(row_count, len(self.df)) > SOCIAL_MEDIA_PCT_CUTOFF:
            print_indented(f"CHOOSING {msg}", style='color(143)', indent_level=2)
            return True
        else:
            print_indented(f"IGNORING {msg}", style='color(155) dim', indent_level=2)
            return False

    def _write_df_to_csv(self) -> None:
        file_basename = f"{self.sheet_id}___{self.worksheet_name}.csv.gz".replace('/', '_slash_')
        file_path = path.join(GZIPPED_CSV_DIR, file_basename)
        print_indented(f"Writing sheet to CSV: '{file_path}'", style='dim')

        if False and path.isfile(file_path):
            console.print(f"File already exists: '{file_path}', skipping...")
        else:
            self.df.to_csv(file_path, index=False, compression=GZIP_COMPRESSION_ARGS)

    def _print_extraction_stats(self) -> None:
        invalid_row_msgs = [
            f"{self.invalid_address_count} invalid",
            f"{self.mismatch_count} mismatches",
            f"{self.null_address_count} null addresses",
        ]

        invalid_msg = ', '.join(invalid_row_msgs)
        valid_row_count = self.df_length - self.invalid_address_count - self.mismatch_count - self.null_address_count
        console.print(f"Total rows: {self.df_length}, valid rows: {valid_row_count} ({invalid_msg})")

