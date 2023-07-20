import time
import random

import global_constants as gc

from loguru import logger

from mute.mute import MuteIO
from nft.mint_nft import Minter
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

        exchange = gc.EXCHANGES[random.randint(0, 3)]  # В данный момент SpaceFi(№3) лагает

        if exchange == 'SyncSwap':
            swapper = SyncSwap(proxies=proxies)
        elif exchange == 'SpaceFi':
            swapper = SpaceFi(proxies=proxies)
        elif exchange == 'Velocore':
            swapper = Velocore(proxies=proxies)
        else:
            swapper = MuteIO(proxies=proxies)

        amount = False
        token0 = gc.ETH
        swap_tokens = gc.SWAP[exchange].copy()

        while not amount and len(swap_tokens) != 0:
            token1 = random.choice(swap_tokens)
            amount = swapper.start_swap(key=key, token0=token0, token1=token1, pub_key=True, exchange=exchange)

            if not amount:
                swap_tokens.remove(token1)

        if gc.SWAP_BACK and len(swap_tokens) != 0:
            delay = random.randint(gc.DELAY1[0], gc.DELAY1[1])
            logger.info(f"Swap back. Wait {delay}")
            amount = amount / 10 ** 18
            time.sleep(delay)

            swapper.start_swap(key=key, token0=token1, token1=token0, amount=amount)

        delay = random.randint(gc.DELAY2[0], gc.DELAY2[1])
        logger.info(f"Go to deposit liquidity. Wait {delay}")
        time.sleep(delay)

        if exchange == 'SyncSwap':
            swapper.add_liquidity(token1=token0, key=key)
        else:
            result = False
            liq_tokens = gc.LIQ[exchange].copy()

            while not result and len(liq_tokens) != 0:

                token0 = random.choice(liq_tokens)
                result = swapper.add_liquidity(token0=token0, key=key)

                if not result:
                    liq_tokens.remove(token0)

        delay = random.randint(gc.DELAY3[0], gc.DELAY3[1])

        shit_coin = random.choice(gc.SHIT_COINS)
        logger.info(f"Go to buy shit coin. Wait {delay}")
        time.sleep(delay)

        buy_shitcoin(shit_coin=shit_coin, key=key, proxies=proxies)

        delay = random.randint(gc.DELAY4[0], gc.DELAY4[1])
        logger.info(f"Go to mint NFT. Wait {delay}")

        minter = Minter(proxies=proxies)
        minter.start_mint(key=key)

        delay = random.randint(gc.DELAY5[0], gc.DELAY5[1])
        logger.info(f"Change wallets. Wait {delay}")
        time.sleep(delay)


if __name__ == '__main__':
    start()
