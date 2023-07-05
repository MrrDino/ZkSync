import json
import web3
import time
import random
import eth_abi

import constants as cst

from web3 import Web3
from modules.helper import pre_check
from abis.erc20 import ERC20_ABI
from abis.router import ROUTER_ABI
from abis.factory import FACTORY_ABI
from web3.types import TxParams, ChecksumAddress
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from modules.global_constants import TIMEOUT, MIN_AMOUNT, MAX_AMOUNT


class SyncSwap:

    def __init__(self):
        pass

    def start(self):

        check = False

        while not check:

            check, keys, proxies = pre_check()

            if not check:
                time.sleep(TIMEOUT)

        for key, proxy in zip(keys, proxies):

            w3 = self.connect()
            account = self.get_account(w3=w3, key=key)
            w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
            amount = int(random.uniform(MIN_AMOUNT, MAX_AMOUNT) * 10 ** 18)

            if not self.check_balance(w3=w3, wallet=account.address, amount=amount):
                continue

    def check_swap(self, key: str):
        """Функция для проверки tokens swap"""

        w3 = self.connect()
        account = self.get_account(w3=w3, key=key)
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))
        amount = int(0.00252 * 10 ** 18)

        self.make_swap(w3=w3, amount=amount, account=account)

    def make_swap(
            self,
            w3: Web3,
            amount: int,
            account: LocalAccount,
            token0: str = cst.ETH,
            token1: str = cst.USDC
    ):
        """Функция выполнения обмена"""

        signer = account.address
        token0 = Web3.to_checksum_address(token0)
        token1 = Web3.to_checksum_address(token1)
        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)
        pool = self.get_contract(w3=w3, address=cst.POOL_FACTORY, abi=FACTORY_ABI)
        pool_address = pool.functions.getPool(token0, token1).call()

        try:
            approved_tx = self.approve_swap(
                w3=w3,
                amount=amount,
                signer=account,
                spender=cst.ROUTER,
                token=token0,
            )
            time.sleep(50)

            approve_status = self.check_tx(w3=w3, tx_hex=approved_tx)
            print(approve_status)
        except Exception as err:
            print(err)

        steps = [
            {
                "pool": pool_address,
                "data": eth_abi.encode(
                    ["address", "address", "uint8"],
                    [token0, signer, cst.WITHDRAW_MODE]
                ),
                "callback": cst.ZERO_ADDRESS,
                "callbackData": '0x'
            }
        ]

        paths = [{'steps': steps, 'tokenIn': token0, 'amountIn': amount}]

        tx = self.create_swap_tx(w3=w3, paths=paths, router=router, wallet=signer)
        signed_tx = account.sign_transaction(transaction_dict=tx)

        try:
            swap_tx = w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = w3.eth.wait_for_transaction_receipt(swap_tx)
            print(swap_tx.hex())
            print(tx_rec)
            time.sleep(50)
        except BaseException as err:
            print(err)

    def check_balance(self, w3: Web3, wallet: str, amount: float) -> bool:
        """Функция проверки баланса"""

        wallet = self.to_address(address=wallet)
        eth_balance = w3.eth.get_balance(wallet) / 10 ** 18

        if eth_balance < amount:
            return False

        return True

    def get_contract(self, w3: web3.Web3, address: str, abi: list) -> web3.contract.Contract:
        """Функция получения пула"""

        address = self.to_address(address=address)
        abi = json.dumps(abi)

        pool = w3.eth.contract(address=address, abi=abi)
        return pool

    @staticmethod
    def approve_swap(
            spender: ChecksumAddress,
            token: ChecksumAddress,
            signer: LocalAccount,
            amount: int,
            w3: Web3
    ) -> str:
        """Функция утверждения использования средств"""

        token_contract = w3.eth.contract(address=token, abi=ERC20_ABI)
        allowance = token_contract.functions.allowance(signer.address, spender).call()

        if allowance < amount:
            max_amount = Web3.to_wei(2 ** 64 - 1, 'ether')

            transaction = token_contract.functions.approve(spender, max_amount).build_transaction({
                'from': signer.address,
                'gas': 3_000_000,
                'gasPrice': w3.eth.gas_price,
                'nonce': w3.eth.get_transaction_count(signer.address)
            })

            approve_tx = signer.sign_transaction(transaction)
            tx = w3.eth.send_raw_transaction(approve_tx.rawTransaction)

            return tx.hex()

    @staticmethod
    def create_swap_tx(
            router: web3.contract.Contract,
            wallet: ChecksumAddress,
            paths: list,
            w3: Web3,
    ) -> TxParams:

        txn = router.functions.swap(
            paths,
            0,
            int(time.time()) + 1800,
        ).build_transaction({
            'from': wallet,
            'gas': 3_000_000,
            'gasPrice': w3.eth.gas_price,
            'nonce': w3.eth.get_transaction_count(wallet),
        })

        return txn

    @staticmethod
    def check_tx(w3: Web3, tx_hex) -> int:
        """Функция проверки транзакции"""

        tx = w3.eth.get_transaction_receipt(transaction_hash=tx_hex)
        print(tx)

        return tx['status']

    @staticmethod
    def to_address(address: str) -> web3.main.ChecksumAddress or None:
        """Функция преобразования адреса в правильный"""

        try:
            return web3.Web3.to_checksum_address(value=address)
        except Exception:
            print(f"Invalid address convert {address}")

    @staticmethod
    def get_account(w3: Web3, key: str) -> LocalAccount:

        account = w3.eth.account.from_key(key)
        return account

    @staticmethod
    def connect() -> Web3:
        """Функция подключения к ноде"""

        w3 = Web3(Web3.HTTPProvider(endpoint_uri=cst.RPC_NODE))

        if w3.is_connected():
            return w3
