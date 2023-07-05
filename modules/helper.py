import os
import time
import functools

import modules.global_constants as cst

from web3 import Web3


def check_gas() -> bool:
    """Функция проверки газа в сети ETH"""

    w3 = Web3(Web3.HTTPProvider(cst.ETH_NODE))
    gas_price = w3.eth.gas_price / 10 ** 9

    if gas_price > cst.MAX_GAS:
        return False

    return True


def check_proxies(proxies: list, keys: list) -> bool:
    """Функция проверки к-ва ключей и прокси"""

    if len(proxies) < len(keys):
        return False

    return True


def get_txt_info(filename: str) -> list:
    """Функция получения ключей из keys.txt"""

    keys = list()
    path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        'configs',
        filename
    )

    with open(path, 'r') as file:
        for line in file:
            keys.append(line.rstrip('\n'))
        file.close()

    return keys


def pre_check() -> [bool, list, list]:
    """Функция предварительной проверки"""

    check = False
    keys = get_txt_info(filename='keys.txt')
    proxies = get_txt_info(filename='proxies.txt')

    proxy_check = check_proxies(proxies=proxies, keys=keys)
    gas_check = check_gas()

    if all([proxy_check, gas_check]):
        check = True

    return [check, keys, proxies]


def check_connection(w3: Web3) -> bool:
    """Функция проверки соединения"""

    return w3.is_connected()


def retry(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        while True:
            try:
                return func(*args, **kwargs)
            except Exception:
                # conn = check_connection(w3=kwargs['w3'])
                #
                # if not conn:
                #     return False  # нет подключения

                time.sleep(45)

    return wrapper
