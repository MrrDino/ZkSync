from . import constants as cst
from syncswap.syncswap import SyncSwap


def buy_shitcoin(shit_coin: str, key: str, proxies: list):
    """Функция покупки шиткоинов"""

    sf = SyncSwap(proxies=proxies)
    sf.start_swap(key=key, token0=cst.ETH, token1=shit_coin, mode=2)
