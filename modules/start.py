import time
import random

import global_constants as gc

from loguru import logger

from mute.mute import MuteIO
from spacefi.spacefi import SpaceFi
from velocore.velocore import Velocore
from syncswap.syncswap import SyncSwap
from shitcoins.shit_coins import buy_shitcoin
from helper import get_txt_info, check_gas, check_proxies


def start():

    check_proxy = False

    while not check_proxy:

        keys = get_txt_info('keys.txt')
        proxies = get_txt_info('proxies.txt')
        check_proxy = check_proxies(proxies=proxies, keys=keys)

        if not check_proxy:
            logger.info(f'Insufficient number of proxies. Wait {gc.TIMEOUT} sec.')
            time.sleep(gc.TIMEOUT)

    for key in keys:
        gas = False

        while not gas:
            gas = check_gas()

            if not gas:
                logger.info(f'High gas. Wait {gc.TIMEOUT} sec.')
                time.sleep(gc.TIMEOUT)

        exchange = gc.EXCHANGES[random.randint(0, 2)]  # В данный момент SpaceFi(№3) лагает

        if exchange == 'SyncSwap':
            swapper = SyncSwap(proxies=proxies)
        elif exchange == 'SpaceFi':
            swapper = SpaceFi(proxies=proxies)
        elif exchange == 'Velocore':
            swapper = Velocore(proxies=proxies)
        else:
            swapper = MuteIO(proxies=proxies)

        token0 = gc.ETH
        token1 = random.choice(gc.SWAP[exchange])

        amount = swapper.start_swap(key=key, token0=token0, token1=token1, pub_key=True, exchange=exchange)

        if gc.SWAP_BACK:
            delay = random.randint(gc.DELAY1[0], gc.DELAY1[1])
            logger.info(f"Swap back. Wait {delay}")
            amount = amount / 10 ** 18
            time.sleep(delay)

            swapper.start_swap(key=key, token0=token1, token1=token0, amount=amount)

        delay = random.randint(gc.DELAY2[0], gc.DELAY2[1])
        logger.info(f"Go to deposit liquidity. Wait {delay}")
        time.sleep(delay)

        token0 = random.choice(gc.LIQ[exchange])

        if exchange == 'SyncSwap':
            swapper.add_liquidity(token1=token0, key=key)
        else:
            swapper.add_liquidity(token0=token0, key=key)

        delay = random.randint(gc.DELAY2[0], gc.DELAY2[1])
        shit_coin = random.choice(gc.SHIT_COINS)
        logger.info(f"Go to buy shit coin. Wait {delay}")
        time.sleep(delay)

        buy_shitcoin(shit_coin=shit_coin, key=key, proxies=proxies)

        delay = random.randint(gc.DELAY2[0], gc.DELAY2[1])
        logger.info(f"Change wallets. Wait {delay}")
        time.sleep(delay)


if __name__ == '__main__':
    start()
