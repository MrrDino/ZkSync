import time

from spacefi import SpaceFi
from modules.helper import pre_check
from modules.global_constants import TIMEOUT, SWAP_BACK


TKNS = [
    '0x503234F203fC7Eb888EEC8513210612a43Cf6115',  # LUSD,
    '0x8e86e46278518efc1c5ced245cba2c7e3ef11557',  # USD+,
    '0xb4c1544cb4163f4c2eca1ae9ce999f63892d912a',  # FRAX,
]


def start():

    check = False
    sf = SpaceFi()

    # while not check:
    #     check, proxies, keys = pre_check()
    #     time.sleep(TIMEOUT)

    keys = ['f19f167dc4e90b7aec96532c508245beac79af1e783dc9bb29d046ce9d9ccfcb']
    proxies = [1]
    # ^- если нужно быстро протестить, не дожидаясь газа, и, не добавляя ключи

    for tk in TKNS:
        # нужно добавить прокси
        key = keys[0]
        token0 = '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'
        token1 = tk
        print(tk)

        amount = sf.start_swap(
            token0=token0,
            token1=token1,
            key=key
        )

        if SWAP_BACK:
            amount = amount / 10 ** 18

            sf.start_swap(
                amount=amount,
                token0=token1,
                token1=token0,
                key=key
            )


if __name__ == '__main__':
    start()
