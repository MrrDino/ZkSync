import time
import random
import asyncio

import settings as conf
import global_constants as gc

from loguru import logger
from threading import Semaphore, Thread

from mute.mute import MuteIO
from izumi.izumi import Izumi
from nft.mint_nft import Minter
from spacefi.spacefi import SpaceFi
from velocore.velocore import Velocore
from syncswap.syncswap import SyncSwap
from maverick.maverick import Maverick
from pancakeswap.pancake import PancakeSwap
from shitcoins.shit_coins import buy_shitcoin
from helper import get_txt_info, check_gas, check_proxies, get_keys, get_exchange, wait, wait_sync, SimpleW3


s = Semaphore(conf.STREAMS)


async def start(proxies: list, keys: list):

    for key in keys:
        gas = False

        while not gas:
            gas = check_gas()

            if not gas:
                logger.info(f'High gas.')
                await wait(_time=conf.TIMEOUT)

        actions = shuffle_actions()
        swapper, swap_exchange = get_exchange_by_act(
            action="swap",
            proxies=proxies
        )
        liqer, liq_exchange = get_exchange_by_act(
            action='liq',
            proxies=proxies
        )
        success, amount, token1 = None, None, None

        for action in actions:

            if gc.ACTIONS_[action] == "swap":
                success, amount, token1 = await swap_module(
                    key=key,
                    swapper=swapper,
                    exchange=swap_exchange
                )
            elif gc.ACTIONS_[action] == "swap_back":
                await swap_back(
                    key=key,
                    token1=token1,
                    amount=amount,
                    swapper=swapper,
                    exchange=swap_exchange
                )
            elif gc.ACTIONS_[action] == "liq":
                await add_liq(exchange=liq_exchange, liqer=liqer, key=key)
            elif gc.ACTIONS_[action] == "nft":
                await mint(key=key, proxies=proxies)
            elif gc.ACTIONS_[action] == "shit":
                await buy_shit(key=key, proxies=proxies)

        delay = random.randint(conf.DELAY5[0], conf.DELAY5[1])
        logger.info(f"Change wallet.")
        await wait(_time=delay)


async def swap_module(swapper: SimpleW3, exchange: str, key: str) -> [bool, int, str]:
    """Функция произведения свапа токена ETH -> stable"""

    amount = False
    token0 = gc.ETH
    swap_tokens = gc.SWAP[exchange].copy()

    while not amount and len(swap_tokens) != 0:
        token1 = random.choice(swap_tokens)

        amount = await swapper.start_swap(
            key=key,
            pub_key=True,
            token0=token0,
            token1=token1,
            action="swap",
            exchange=exchange
        )

        if not amount:
            swap_tokens.remove(token1)

    success = True if swap_tokens != 0 else False

    return [success, amount, token1]


async def swap_back(amount: int, swapper: SimpleW3, exchange: str, token1: str, key: str):
    """Функция произведения свапа в обратную сторону"""

    token0 = gc.ETH
    amount = amount / 10 ** 18

    delay = random.randint(conf.DELAY1[0], conf.DELAY1[1])
    logger.info(f"Swap back")
    await wait(_time=delay)

    await swapper.start_swap(
        key=key,
        pub_key=True,
        token0=token1,
        token1=token0,
        amount=amount,
        exchange=exchange,
        action="swap back",
    )


async def add_liq(exchange: str, liqer: SimpleW3, key: str):
    """Функция добавления ликвидности"""

    delay = random.randint(conf.DELAY2[0], conf.DELAY2[1])
    logger.info(f"Go to deposit liquidity")
    await wait(_time=delay)

    liq_tokens = gc.LIQ[exchange].copy()

    if exchange == 'SyncSwap':
        token0 = random.choice(liq_tokens)

        await liqer.add_liquidity(token1=token0, key=key, exchange=exchange)
    else:
        result = False

        while not result and len(liq_tokens) != 0:

            token0 = random.choice(liq_tokens)
            result = await liqer.add_liquidity(token0=token0, key=key, exchange=exchange)

            if not result:
                liq_tokens.remove(token0)


async def mint(key: str, proxies: list):
    """Функция минта NFT"""

    delay = random.randint(conf.DELAY4[0], conf.DELAY4[1])
    logger.info(f"Go to mint NFT")
    await wait(_time=delay)

    minter = Minter(proxies=proxies)
    await minter.start_mint(key=key)


async def buy_shit(key: str, proxies: list):
    """Функция покупки шиткоина"""

    delay = random.randint(conf.DELAY3[0], conf.DELAY3[1])
    shit_coin = random.choice(gc.SHIT_COINS)
    logger.info(f"Go to buy shit coin")
    await wait(_time=delay)

    await buy_shitcoin(shit_coin=shit_coin, key=key, proxies=proxies)


def shuffle_actions() -> list:
    """Функция рандомизации действий"""

    act_list = list()

    actions = [
        conf.NEED_SWAP,
        conf.SWAP_BACK,
        conf.NEED_LIQ,
        conf.NEED_NFT,
        conf.NEED_SHITCOIN
    ]

    for num, action in enumerate(actions):
        if action:
            act_list.append(num)

    random.shuffle(act_list)

    return act_list


def get_exchange_by_act(action: str, proxies: list) -> [SimpleW3, str]:
    """Функция получния биржа по действию"""

    exchange = get_exchange(action=action)

    if exchange == 'Izumi':
        swapper = Izumi(proxies=proxies)
    elif exchange == 'Mute':
        swapper = MuteIO(proxies=proxies)
    elif exchange == 'SpaceFi':
        swapper = SpaceFi(proxies=proxies)
    elif exchange == 'SyncSwap':
        swapper = SyncSwap(proxies=proxies)
    elif exchange == 'Velocore':
        swapper = Velocore(proxies=proxies)
    elif exchange == 'Maverick':
        swapper = Maverick(proxies=proxies)
    else:
        swapper = PancakeSwap(proxies=proxies)

    return [swapper, exchange]


def start_thread(keys: list, proxies: list):

    s.acquire()
    asyncio.run(start(proxies=proxies, keys=keys))
    time.sleep(2)
    s.release()


def starter():

    check_proxy = False

    while not check_proxy:
        keys = get_txt_info('keys.txt')
        proxies = get_txt_info('proxies.txt')
        check_proxy = check_proxies(proxies=proxies, keys=keys)

        if not check_proxy:
            logger.info(f'Insufficient number of proxies.')
            wait_sync(_time=conf.TIMEOUT)

    keys_list = list(get_keys(items=keys, n=conf.STREAMS))
    threads = [Thread(target=start_thread, args=(ks, proxies)) for ks in keys_list]

    for t in threads:
        t.start()

    for t in threads:
        t.join()


if __name__ == '__main__':
    starter()