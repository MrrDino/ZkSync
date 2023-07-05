import time

from syncswap import SyncSwap
from modules.helper import pre_check
from modules.global_constants import TIMEOUT, SWAP_BACK


def start(token0: str, token1: str):

    check = False
    sc = SyncSwap()

    while not check:
        check, proxies, keys = pre_check()
        time.sleep(TIMEOUT)

    # keys = ['7db340b35b7f8bece3ff7299df1d711130ebc5472e66f91b8aa31f1ba425f0ff']
    # proxies = [1]
    # ^- если нужно быстро протестить, не дожидаясь газа, и, не добавляя ключи

    for key, proxy in zip(keys, proxies):
        # нужно добавить прокси

        amount = sc.start_swap(
            token0=token0,
            token1=token1,
            key=key
        )

        if SWAP_BACK:
            amount = amount / 10 ** 18

            sc.start_swap(
                amount=amount,
                token0=token1,
                token1=token0,
                key=key
            )


if __name__ == '__main__':
    start(
        token0='0x5aea5775959fbc2557cc8789bc1bf90a239d9a91',
        token1='0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'
    )
