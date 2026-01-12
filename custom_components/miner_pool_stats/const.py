"""Constants for the Miner Pool Stats integration."""

from enum import StrEnum

DOMAIN = "miner_pool_stats"

CONF_TITLE = "title"
CONF_POOL_KEY = "pool_key"
CONF_POOL_NAME = "pool_name"
CONF_POOL_URL = "pool_url"
CONF_ADDRESS = "address"
CONF_FRIENDLY_NAME = "friendly_name"
CONF_COIN_KEY = "coin_key"
CONF_COIN_NAME = "coin_name"
CONF_UNIQUE_ID = "unique_id"
CONF_SOURCE = "source"
CONF_API_KEY = "api_key"
CONF_ACCOUNT_ID = "account_id"

POOL_SOURCE_PUBLIC_POOL_KEY = "public_pool"
POOL_SOURCE_PUBLIC_POOL_NAME = "Public Pool"
POOL_SOURCE_F2_POOL_KEY = "f2_pool"
POOL_SOURCE_F2_POOL_NAME = "f2pool"
POOL_SOURCE_SOLO_POOL_KEY = "solo_pool"
POOL_SOURCE_SOLO_POOL_NAME = "SoloPool.org"
POOL_SOURCE_COIN_MINERS_KEY = "coin_miners"
POOL_SOURCE_COIN_MINERS_NAME = "Coin-Miners.info"
POOL_SOURCE_CK_POOL_KEY = "ck_pool"
POOL_SOURCE_CK_POOL_NAME = "CKPool"
POOL_SOURCE_MINING_DUTCH_KEY = "mining_dutch"
POOL_SOURCE_MINING_DUTCH_NAME = "Mining Dutch"
POOL_SOURCE_MINING_CORE_KEY = "mining_core"
POOL_SOURCE_MINING_CORE_NAME = "Mining Core"

WALLET_ADDRESS = "Wallet Address"
WORKER = "Worker"

KEY_TOTAL_PAID = "total_paid"
KEY_CURRENT_BALANCE = "current_balance"
KEY_WORKER_COUNT = "worker_count"
KEY_BEST_DIFFICULTY = "best_difficulty"
KEY_HASH_RATE = "hash_rate"
KEY_START_TIME = "start_time"
KEY_LAST_SEEN = "last_seen"

UNIT_WORKER_COUNT = "workers"
UNIT_HASH_RATE = "GH/s"
UNIT_DIFFICULTY = "difficulty"


class CryptoCoin(StrEnum):
    """List of crypto coins."""

    BTC = "btc"
    BCH = "bch"
    ALEO = "aleo"
    BELLS = "bells"
    BTG = "btg"
    CFX = "cfx"
    CKB = "ckb"
    CLORE = "clore"
    DASH = "dash"
    DOGE = "doge"
    ELA = "ela"
    EHHW = "ehhw"
    FB = "fb"
    ERG = "erg"
    ETC = "etc"
    ETHW = "ethw"
    HTR = "htr"
    IRON = "iron"
    JKC = "jkc"
    KAS = "kas"
    KDA = "kda"
    LTC = "ltc"
    LKY = "lky"
    NEOX = "neox"
    NEXA = "nexa"
    NMC = "nmc"
    OCTA = "octa"
    PEP = "pep"
    RVN = "rvn"
    SDR = "sdr"
    XNA = "xna"
    XEC = "xec"
    XEL = "xel"
    XMR = "xmr"
    ZEC = "zec"
    ZEN = "zen"
    ZEPH = "zeph"


POOL_SOURCE_F2_POOL_COINS = [
    CryptoCoin.BTC,
    CryptoCoin.BCH,
    CryptoCoin.ALEO,
    CryptoCoin.BELLS,
    CryptoCoin.CFX,
    CryptoCoin.CKB,
    CryptoCoin.DASH,
    CryptoCoin.ELA,
    CryptoCoin.ETC,
    CryptoCoin.EHHW,
    CryptoCoin.FB,
    CryptoCoin.IRON,
    CryptoCoin.HTR,
    CryptoCoin.JKC,
    CryptoCoin.KDA,
    CryptoCoin.KAS,
    CryptoCoin.LTC,
    CryptoCoin.LKY,
    CryptoCoin.NEXA,
    CryptoCoin.NMC,
    CryptoCoin.PEP,
    CryptoCoin.ZEC,
    CryptoCoin.ZEN,
]

POOL_SOURCE_SOLO_POOL_COINS = [
    CryptoCoin.BTC,
    CryptoCoin.BCH,
    CryptoCoin.BTG,
    CryptoCoin.CLORE,
    CryptoCoin.ERG,
    CryptoCoin.ETC,
    CryptoCoin.ETHW,
    CryptoCoin.FB,
    CryptoCoin.KAS,
    CryptoCoin.NEOX,
    CryptoCoin.OCTA,
    CryptoCoin.RVN,
    CryptoCoin.SDR,
    CryptoCoin.XNA,
    CryptoCoin.XEC,
    CryptoCoin.XEL,
    CryptoCoin.XMR,
    CryptoCoin.ZEPH,
]

POOL_SOURCE_MINING_DUTCH_POOL_COINS = [
    CryptoCoin.BTC,
    CryptoCoin.BCH,
    CryptoCoin.LTC,
]

POOL_SOURCE_MINING_CORE_POOL_COINS = [
    CryptoCoin.BCH,
    CryptoCoin.DOGE,
]
