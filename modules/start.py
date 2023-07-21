import time
import random
import asyncio

import global_constants as gc

from loguru import logger

from mute.mute import MuteIO
from nft.mint_nft import Minter
from spacefi.spacefi import SpaceFi
from velocore.velocore import Velocore
from syncswap.syncswap import SyncSwap
from shitcoins.shit_coins import buy_shitcoin
from helper import get_txt_info, check_gas, check_proxies, get_keys


async def start(proxies: list, keys: list):

    for key in keys:
        gas = False

        while not gas:
            gas = check_gas()

            if not gas:
                logger.info(f'High gas. Wait {gc.TIMEOUT} sec.')
                await asyncio.sleep(gc.TIMEOUT)

        exchange = gc.EXCHANGES[random.randint(0, 3)]

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
            amount = await swapper.start_swap(key=key, token0=token0, token1=token1, pub_key=True, exchange=exchange)

            if not amount:
                swap_tokens.remove(token1)

        if gc.SWAP_BACK and len(swap_tokens) != 0:
            delay = random.randint(gc.DELAY1[0], gc.DELAY1[1])
            logger.info(f"Swap back. Wait {delay} sec.")
            amount = amount / 10 ** 18
            await asyncio.sleep(delay)

            await swapper.start_swap(key=key, token0=token1, token1=token0, amount=amount)

        if gc.NEED_LIQ:

            delay = random.randint(gc.DELAY2[0], gc.DELAY2[1])
            logger.info(f"Go to deposit liquidity. Wait {delay} sec.")
            await asyncio.sleep(delay)

            liq_tokens = gc.LIQ[exchange].copy()

            if exchange == 'SyncSwap':
                token0 = random.choice(liq_tokens)

                await swapper.add_liquidity(token1=token0, key=key)
            else:
                result = False

                while not result and len(liq_tokens) != 0:

                    token0 = random.choice(liq_tokens)
                    result = await swapper.add_liquidity(token0=token0, key=key)

                    if not result:
                        liq_tokens.remove(token0)

        delay = random.randint(gc.DELAY3[0], gc.DELAY3[1])
        shit_coin = random.choice(gc.SHIT_COINS)
        logger.info(f"Go to buy shit coin. Wait {delay} sec.")
        await asyncio.sleep(delay)

        await buy_shitcoin(shit_coin=shit_coin, key=key, proxies=proxies)

        delay = random.randint(gc.DELAY4[0], gc.DELAY4[1])
        logger.info(f"Go to mint NFT. Wait {delay} sec.")
        await asyncio.sleep(1)

        minter = Minter(proxies=proxies)
        await minter.start_mint(key=key)

        delay = random.randint(gc.DELAY5[0], gc.DELAY5[1])
        logger.info(f"Change wallets. Wait {delay} sec.")
        await asyncio.sleep(delay)


def starter():

    check_proxy = False

    while not check_proxy:

        keys = get_txt_info('keys.txt')
        proxies = get_txt_info('proxies.txt')
        check_proxy = check_proxies(proxies=proxies, keys=keys)

        if not check_proxy:
            logger.info(f'Insufficient number of proxies. Wait {gc.TIMEOUT} sec.')
            time.sleep(gc.TIMEOUT)

    tasks = list()
    keys_list = list(get_keys(items=keys, n=gc.DIVIDER))

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    for key in keys_list:
        tasks.append(loop.create_task(start(proxies, key)))

    tasks_for_wait = asyncio.wait(tasks)
    loop.run_until_complete(tasks_for_wait)
    loop.close()


if __name__ == '__main__':
    starter()
