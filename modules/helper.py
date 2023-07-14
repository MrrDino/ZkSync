import os
import sys
import time
import web3
import json
import random
import functools

import modules.global_constants as cst

from web3 import Web3
from loguru import logger
from hexbytes.main import HexBytes
from web3.types import ChecksumAddress
from eth_account.signers.local import LocalAccount

from modules.general_abis.erc20 import ERC20_ABI


try:
    logger.remove(0)
    logger.add(sys.stdout, format="{time:D MMMM HH:mm:ss} | {message}")
except Exception:
    pass


def get_gas() -> float:
    """Функция получения газа в сети ETH"""

    w3 = Web3(Web3.HTTPProvider(cst.ETH_NODE))
    gas_price = w3.eth.gas_price / 10 ** 9

    return round(gas_price, 2)


def check_gas() -> bool:
    """Функция проверки газа в сети ETH"""

    gas_price = get_gas()

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


class SimpleW3:

    def __init__(self):
        self.node_url = 'https://rpc.ankr.com/zksync_era'

    # def connect(self, proxy: str) -> Web3:
    #     """Функция подключения к ноде"""
    #
    #     proxies = dict(http=f"http://{proxy}", https=f"http://{proxy}")
    #     w3 = Web3(Web3.HTTPProvider(
    #         endpoint_uri=self.node_url,
    #         request_kwargs={'proxies': proxies}
    #     ))
    #
    #     if w3.is_connected():
    #         return w3

    def connect(self) -> Web3:
        """Функция подключения к ноде"""

        w3 = Web3(Web3.HTTPProvider(endpoint_uri=self.node_url))

        if w3.is_connected():
            return w3

    def get_contract(self, w3: web3.Web3, address: str, abi: list) -> web3.contract.Contract:
        """Функция получения пула"""

        address = self.to_address(address=address)
        abi = json.dumps(abi)

        pool = w3.eth.contract(address=address, abi=abi)
        return pool

    @staticmethod
    def to_address(address: str) -> web3.main.ChecksumAddress or None:
        """Функция преобразования адреса в правильный"""

        try:
            return web3.Web3.to_checksum_address(value=address)
        except Exception:
            logger.error(f"Invalid address convert {address}")

    @staticmethod
    def get_account(w3: Web3, key: str) -> LocalAccount:

        account = w3.eth.account.from_key(key)
        return account

    def get_amount(self, w3: Web3, wallet: str) -> int:
        """Функция проверки баланса"""

        wallet = self.to_address(address=wallet)
        eth_balance = w3.eth.get_balance(wallet)
        min_amount = cst.MIN_AMOUNT * 10 ** 18
        max_amount = cst.MAX_AMOUNT * 10 ** 18

        if eth_balance < min_amount:  # простая проверка на баланс
            return 0
        elif eth_balance < max_amount:
            eth_balance = int(eth_balance * .9)
            return random.randrange(min_amount, eth_balance)
        else:
            return random.randrange(min_amount, max_amount)

    @staticmethod
    def approve_swap(
            sign_addr: ChecksumAddress,
            spender: ChecksumAddress,
            token: ChecksumAddress,
            signer: LocalAccount,
            amount: int,
            w3: Web3
    ) -> HexBytes:
        """Функция утверждения использования средств"""

        token_contract = w3.eth.contract(address=token, abi=ERC20_ABI)
        allowance = token_contract.functions.allowance(sign_addr, spender).call()

        if allowance < amount:
            max_amount = Web3.to_wei(2 ** 64 - 1, 'ether')

            transaction = token_contract.functions.approve(spender, max_amount).build_transaction({
                'from': sign_addr,
                'gas': 3_000_000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(sign_addr)
            })

            approve_tx = signer.sign_transaction(transaction)
            time.sleep(30)

            tx = w3.eth.send_raw_transaction(approve_tx.rawTransaction)

            return tx


def retry(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        while True:
            try:
                return func(*args, **kwargs)
            except Exception as err:
                logger.error(f"\33[{31}mRetry: {err}\033[0m")

                time.sleep(45)

    return wrapper
