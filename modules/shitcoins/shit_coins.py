import constants as cst

from modules.spacefi.spacefi import SpaceFi


def buy_shitcoin(shit_coin: str, key: str):

    sf = SpaceFi()
    sf.start_swap(key=key, token0=cst.ETH, token1=shit_coin)
