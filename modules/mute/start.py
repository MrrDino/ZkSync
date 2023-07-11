import time

from mute import MuteIO
from modules.helper import pre_check
from modules.global_constants import TIMEOUT, SWAP_BACK


def start(token0: str, token1: str):

    check = False
    mt = MuteIO()

    # while not check:
    #     check, proxies, keys = pre_check()
    #     time.sleep(TIMEOUT)

    keys = ['f19f167dc4e90b7aec96532c508245beac79af1e783dc9bb29d046ce9d9ccfcb']
    proxies = [1]
    # ^- если нужно быстро протестить, не дожидаясь газа, и, не добавляя ключи

    for key, proxy in zip(keys, proxies):
        # нужно добавить прокси

        # amount = mt.start_swap(
        #     token0=token0,
        #     token1=token1,
        #     key=key
        # )
        #
        # if SWAP_BACK:
        #     amount = amount / 10 ** 18
        #
        #     mt.start_swap(
        #         amount=amount,
        #         token0=token1,
        #         token1=token0,
        #         key=key
        #     )

        mt.add_liquidity(token0=token1, key=key)


if __name__ == '__main__':
    start(
        token0='0x5aea5775959fbc2557cc8789bc1bf90a239d9a91',
        token1='0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4'
    )
