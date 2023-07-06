import time

from mute import MuteIO
from modules.helper import pre_check
from modules.global_constants import TIMEOUT, SWAP_BACK


def start(token0: str, token1: str):

    check = False
    mt = MuteIO()

    while not check:
        check, proxies, keys = pre_check()
        time.sleep(TIMEOUT)

    # keys = ['7db340b35b7f8bece3ff7299df1d711130ebc5472e66f91b8aa31f1ba425f0ff']
    # proxies = [1]
    # ^- если нужно быстро протестить, не дожидаясь газа, и, не добавляя ключи

    for key, proxy in zip(keys, proxies):
        # нужно добавить прокси

        amount = mt.start_swap(
            token0=token0,
            token1=token1,
            key=key
        )

        if SWAP_BACK:
            amount = amount / 10 ** 18

            mt.start_swap(
                amount=amount,
                token0=token1,
                token1=token0,
                key=key
            )


if __name__ == '__main__':
    start(
        token0='0x5aea5775959fbc2557cc8789bc1bf90a239d9a91',
        token1='0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4'
    )
