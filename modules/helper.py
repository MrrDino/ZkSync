import os
import sys
import time
import web3
import json
import random
import requests
import functools

import global_constants as cst

from web3 import Web3
from loguru import logger
from hexbytes.main import HexBytes
from web3.types import ChecksumAddress
from requests.adapters import HTTPAdapter, Retry
from eth_account.signers.local import LocalAccount

from general_abis.erc20 import ERC20_ABI


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

    def __init__(self, proxies: list):
        self.url = 'https://api.dexscreener.io/latest/dex/pairs/zksync/'
        self.pool = '0x80115c708E12eDd42E504c1cD52Aea96C547c05c'
        self.node_url = cst.ZK_NODE
        self.proxies = proxies

    def connect(self) -> Web3:
        """Функция подключения к ноде"""

        conn = False

        while not conn:
            proxy = random.choice(self.proxies)
            proxies = dict(http=proxy, https=proxy)
            w3 = Web3(Web3.HTTPProvider(
                endpoint_uri=self.node_url,
                request_kwargs={'proxies': proxies}
            ))
            conn = w3.is_connected()

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

    def get_amount(
            self,
            w3: Web3,
            mode: int,
            wallet: str,
            eth: float = None
    ) -> int or None:
        """Функция проверки баланса"""

        wallet = self.to_address(address=wallet)
        eth_balance = w3.eth.get_balance(wallet)
        min_amount, max_amount = cst.AMOUNTS[mode]

        if mode == 1:
            min_amount = int(min_amount / 100 * eth * 10 ** 18)
            max_amount = int(max_amount / 100 * eth * 10 ** 18)
        else:
            min_amount = int(min_amount * 10 ** 18)
            max_amount = int(max_amount * 10 ** 18)

        if eth_balance < min_amount:  # простая проверка на баланс
            return
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

    def get_decimals(self, w3: Web3, token: ChecksumAddress) -> int:
        """Функция получения количества цифр после запятой"""

        token_contract = self.get_contract(w3=w3, address=token, abi=ERC20_ABI)
        decimals = token_contract.functions.decimals().call()

        return decimals

    def get_eth(
            self,
            w3: Web3,
            abi: list,
            pair_address: ChecksumAddress
    ) -> float:
        """Функция перевода из центов в ETH"""

        pair = self.get_contract(w3=w3, address=pair_address, abi=abi)
        reserves = pair.functions.getReserves().call()
        tkn0 = pair.functions.token0().call()

        if cst.USDC.lower() == tkn0.lower():
            token0_res = reserves[0] / 10 ** cst.USDC_DECS
            token1_res = reserves[1] / 10 ** cst.ETH_DECS
        else:
            token0_res = reserves[1] / 10 ** cst.USDC_DECS
            token1_res = reserves[0] / 10 ** cst.ETH_DECS

        eth = token1_res / token0_res

        return eth

    def check_amount(
            self,
            w3: Web3,
            eth: int,
            f_abi: list,
            p_abi: list,
            token: ChecksumAddress,
            wallet: ChecksumAddress,
            f_address: ChecksumAddress,
            exchange: str = 'NO',
            stable: bool = False
    ) -> bool:
        """Функция проверки наличия суммы на балансе равносильной ETH"""

        token0_res, token1_res, tkn0, decs0, decs1 = self.get_reserves(
            w3=w3,
            p_abi=p_abi,
            f_abi=f_abi,
            token0=token,
            stable=stable,
            exchange=exchange,
            f_address=f_address,
            token1=self.to_address(cst.ETH),
        )

        token_contract = self.get_contract(w3=w3, address=token, abi=ERC20_ABI)
        balance = token_contract.functions.balanceOf(wallet).call() / 10 ** decs0

        token_balance = balance * (token1_res / token0_res)

        if token_balance > (eth / 10 ** 18):
            return True
        else:
            return False

    def get_reserves(
            self,
            w3: Web3,
            f_abi: list,
            p_abi: list,
            stable: bool,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            f_address: ChecksumAddress,
            exchange: str = 'NO'
    ) -> [float, float, ChecksumAddress, int, int]:
        """Функция получения резервов пула"""

        factory = self.get_contract(w3=w3, address=f_address, abi=f_abi)

        if exchange == 'SyncSwap':
            pool_address = factory.functions.getPool(token0, token1).call()
        elif exchange == 'SpaceFi':
            pool_address = factory.functions.getPair(token0, token1).call()
        else:
            pool_address = factory.functions.getPair(token0, token1, stable).call()

        pool = self.get_contract(w3=w3, address=pool_address, abi=p_abi)
        reserves = pool.functions.getReserves().call()

        decs0 = self.get_decimals(w3=w3, token=token0)
        decs1 = self.get_decimals(w3=w3, token=token1)
        tkn0 = pool.functions.token0().call()

        if token0.lower() == tkn0.lower():
            token0_res = reserves[0] / 10 ** decs0
            token1_res = reserves[1] / 10 ** decs1
        else:
            token0_res = reserves[1] / 10 ** decs0
            token1_res = reserves[0] / 10 ** decs1

        return [token0_res, token1_res, tkn0, decs0, decs1]

    @staticmethod
    def deadline() -> int:
        """Функция возвращения параметра deadline"""

        return int(time.time()) + 600

    def get_fee_by_url(self, gas_used: int, gas_price: int) -> float:
        """Функция получения комиссии транзакции в долларах"""

        price = None
        attempts = 5
        amount = (gas_used * gas_price) / 10 ** 18

        client = requests.Session()
        # proxy = random.choice(self.proxies)
        # client.proxies = dict(http=proxy, https=proxy)  мои прокси не проходят
        retries = Retry(
            total=15,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )

        client.mount('http://', HTTPAdapter(max_retries=retries))

        while not price and attempts != 0:
            try:
                response = client.get(url=f"{self.url}{self.pool}")

                if response.status_code != 200:
                    raise Exception

                data = response.json()
                price = float(data['pairs'][0]['priceUsd'])
            except Exception as err:
                logger.error(err)
                attempts -= 1
                time.sleep(2)

        fee_price = amount * price

        return round(fee_price, 2)


def retry(func):

    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        while True:
            try:
                return func(*args, **kwargs)
            except Exception as err:
                logger.error(f"\33[{31}mRetry: {err}\033[0m")
                time.sleep(25)

    return wrapper
