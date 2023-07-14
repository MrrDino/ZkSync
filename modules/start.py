import time
import random

import global_constants as gc

from loguru import logger

from mute.mute import MuteIO
from spacefi.spacefi import SpaceFi
from velocore.velocore import Velocore
from syncswap.syncswap import SyncSwap
from helper import get_txt_info, check_gas
from shitcoins.shit_coins import buy_shitcoin


def start():

    keys = get_txt_info('keys.txt')

    for key in keys:
        gas = False

        while not gas:
            gas = check_gas()

            if not gas:
                logger.info(f'High gas. Wait {gc.TIMEOUT} sec.')
                time.sleep(gc.TIMEOUT)

        exchange = gc.EXCHANGES[random.randint(0, 3)]

        if exchange == 'SyncSwap':
            swapper = SyncSwap()
        elif exchange == 'SpaceFi':
            swapper = SpaceFi()
        elif exchange == 'Velocore':
            swapper = Velocore()
        else:
            swapper = MuteIO()

        token0 = gc.ETH
        token1 = random.choice(gc.SWAP[exchange])
        amount = swapper.start_swap(key=key, token0=token0, token1=token1, pub_key=True, exchange=exchange)

        if gc.SWAP_BACK:
            delay = random.randint(gc.DELAY1[0], gc.DELAY1[1])
            logger.info(f"Swap back. Wait {delay}")
            time.sleep(delay)

            amount = amount / 10 ** 18
            swapper.start_swap(key=key, token0=token1, token1=token0, amount=amount)

        delay = random.randint(gc.DELAY2[0], gc.DELAY2[1])
        logger.info(f"Go to deposit liquidity. Wait {delay}")
        time.sleep(delay)

        token0 = random.choice(gc.LIQ[exchange])
        exchange.add_liquidity(token0=token0, key=key)

        delay = random.randint(gc.DELAY2[0], gc.DELAY2[1])
        logger.info(f"Go to buy shit coin. Wait {delay}")
        time.sleep(delay)

        shit_coin = random.choice(gc.SHIT_COINS)
        buy_shitcoin(shit_coin=shit_coin, key=key)

        delay = random.randint(gc.DELAY2[0], gc.DELAY2[1])
        logger.info(f"Change wallets. Wait {delay}")
        time.sleep(delay)


if __name__ == '__main__':
    start()