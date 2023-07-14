import time

from mute import MuteIO
from modules.helper import pre_check
from modules.global_constants import TIMEOUT, SWAP_BACK


TKNS = [
    '0x8e86e46278518efc1c5ced245cba2c7e3ef11557',  # USD+,
]


def start():

    check = False
    mt = MuteIO()

    # while not check:
    #     check, proxies, keys = pre_check()
    #     time.sleep(TIMEOUT)

    keys = ['7db340b35b7f8bece3ff7299df1d711130ebc5472e66f91b8aa31f1ba425f0ff']
    proxies = [1]
    # ^- если нужно быстро протестить, не дожидаясь газа, и, не добавляя ключи

    for tk in TKNS:
        # нужно добавить прокси
        key = keys[0]
        token0 = '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'
        token1 = tk
        print(tk)

        mt.add_liquidity(token0=token1, key=key)


if __name__ == '__main__':
    start()
