import json
import web3
import time
import random
import eth_abi

import constants as cst

from web3 import Web3

from hexbytes.main import HexBytes
from web3.types import TxParams, ChecksumAddress
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from abis.pool import POOL_ABI
from abis.erc20 import ERC20_ABI
from abis.router import ROUTER_ABI
from abis.factory import FACTORY_ABI
from modules.global_constants import MIN_AMOUNT, MAX_AMOUNT


class SyncSwap:

    def __init__(self):
        pass

    def start_swap(self, key: str, token0: str, token1: str, amount: float = None) -> int or None:
        """Функция для проверки tokens swap"""

        w3 = self.connect()
        account = self.get_account(w3=w3, key=key)
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        if not amount:
            amount = self.get_amount(w3=w3, wallet=account.address)

            if amount == 0:
                return False

            success = self.make_swap(w3=w3, amount=amount, account=account, token0=token0, token1=token1)
            return amount
        else:
            success = self.make_swap(w3=w3, amount=amount, account=account, token0=token0, token1=token1)

    def make_swap(
            self,
            w3: Web3,
            amount: int or float,
            account: LocalAccount,
            token0: str = cst.ETH,
            token1: str = cst.USDC
    ) -> bool:
        """Функция выполнения обмена"""

        signer = account.address
        token0 = self.to_address(token0)
        token1 = self.to_address(token1)
        token_in = cst.TOKENS[token0.lower()]  # если ETH -> поведение меняется)
        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)
        pool = self.get_contract(w3=w3, address=cst.POOL_FACTORY, abi=FACTORY_ABI)
        pool_address = pool.functions.getPool(token0, token1).call()

        #  Если повторный свап -> переводим сумму из ETH в USDC
        if isinstance(amount, float):
            rate = self.get_rate(w3=w3, pool=pool_address, token_ch=token0)
            amount = self.get_swap_amount(amount=amount, rate=rate)

        print(amount)

        if token_in != 'ETH':

            try:
                approved_tx = self.approve_swap(
                    w3=w3,
                    amount=amount,
                    signer=account,
                    spender=cst.ROUTER,
                    token=token0,
                )
                tx_rec = w3.eth.wait_for_transaction_receipt(approved_tx)
                status = tx_rec['status']
                print(f'Tx: {approved_tx.hex()}. Status: {status}')

                time.sleep(50)
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

        paths = [
            {
                'steps': steps,
                'tokenIn': cst.ZERO_ADDRESS if token_in == 'ETH' else token0,
                'amountIn': amount
            }
        ]

        tx = self.create_swap_tx(
            w3=w3,
            paths=paths,
            wallet=signer,
            router=router,
            amount=amount,
            token_in=token_in
        )

        tx.update(
            {
                'gas': w3.eth.estimate_gas(tx),
                'maxFeePerGas': w3.eth.gas_price,
                'maxPriorityFeePerGas': w3.eth.gas_price
            }
        )

        signed_tx = account.sign_transaction(transaction_dict=tx)
        time.sleep(30)

        try:
            swap_tx = w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = w3.eth.wait_for_transaction_receipt(swap_tx)
            status = tx_rec['status']  # будет использоваться для переотправки
            print(f'Tx: {swap_tx.hex()}. Status: {status}')

        except BaseException as err:
            print(err)

        return True

    def get_amount(self, w3: Web3, wallet: str) -> int:
        """Функция проверки баланса"""

        wallet = self.to_address(address=wallet)
        eth_balance = w3.eth.get_balance(wallet)
        min_amount = MIN_AMOUNT * 10 ** 18
        max_amount = MAX_AMOUNT * 10 ** 18

        if eth_balance < min_amount:  # простая проверка на баланс
            return 0
        elif eth_balance < max_amount:
            eth_balance = int(eth_balance * .9)
            return random.randrange(min_amount, eth_balance)
        else:
            return random.randrange(min_amount, max_amount)

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
    ) -> HexBytes:
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
            time.sleep(30)

            tx = w3.eth.send_raw_transaction(approve_tx.rawTransaction)

            return tx

    @staticmethod
    def create_swap_tx(
            router: web3.contract.Contract,
            wallet: ChecksumAddress,
            token_in: str,
            amount: int,
            paths: list,
            w3: Web3,
    ) -> TxParams:

        txn = router.functions.swap(
            paths,
            0,
            int(time.time()) + 1800,
        ).build_transaction({
            'gas': 0,
            'from': wallet,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'value': amount if token_in == 'ETH' else 0,
            'nonce': w3.eth.get_transaction_count(wallet),
        })

        return txn

    def get_rate(self, w3: Web3, pool: ChecksumAddress, token_ch: ChecksumAddress) -> float:
        """Функция получения курса в пуле"""

        contract = self.get_contract(w3=w3, address=pool, abi=POOL_ABI)
        reserves = contract.functions.getReserves().call()
        token0 = contract.functions.token0().call()

        if cst.TOKENS[token0.lower()] == 'ETH':
            usd = int(reserves[1] / 10 ** 6) / int(reserves[0] / 10 ** 18)
        else:
            usd = int(reserves[0] / 10 ** 6) / int(reserves[1] / 10 ** 18)

        usd -= usd * cst.MULTS[token_ch.lower()]

        return usd

    @staticmethod
    def get_swap_amount(amount: float, rate: float, dec: int = 6) -> int:
        """Функция суммы для обмена USDT/USDC"""

        return int(amount * rate * (10 ** dec))

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

