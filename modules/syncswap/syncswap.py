import web3
import time
import eth_abi

import constants as cst

from web3 import Web3
from web3.types import TxParams, ChecksumAddress
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from abis.pool import POOL_ABI
from abis.router import ROUTER_ABI
from modules.helper import SimpleW3
from abis.factory import FACTORY_ABI


class SyncSwap(SimpleW3):

    def start_swap(self, key: str, token0: str, token1: str, amount: float = None) -> int or None:
        """Функция запуска tokens swap для SyncSwap"""

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
    ) -> bool or None:
        """Функция выполнения обмена для SyncSwap"""

        signer = account.address
        pool, token0, token1, pool_address = self.preparing(
            w3=w3,
            token0=token0,
            token1=token1
        )

        if pool_address == cst.ZERO_ADDRESS:
            return

        token_in = cst.TOKENS[token0.lower()]  # если ETH -> поведение меняется
        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)

        #  Если повторный свап -> переводим сумму из ETH в USDC
        if isinstance(amount, float):
            rate = self.get_rate(w3=w3, pool=pool_address, token_ch=token0)
            amount = self.get_swap_amount(amount=amount, rate=rate)

        if token_in != 'ETH':

            try:
                approved_tx = self.approve_swap(
                    w3=w3,
                    token=token0,
                    amount=amount,
                    signer=account,
                    sign_addr=signer,
                    spender=cst.ROUTER,
                )

                if approved_tx:
                    tx_rec = w3.eth.wait_for_transaction_receipt(approved_tx)
                    status = tx_rec['status']
                    print(f'Approve tx: {approved_tx.hex()}. Status: {status}')
                    time.sleep(50)
                else:
                    print("Doesn't need approve")
                    time.sleep(20)
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

    def add_liquidity(self, token0: str, token1: str, key: str):
        """Функция добавления ликвидности"""

        w3 = self.connect()
        token_in = cst.TOKENS[token0.lower()]  # если ETH -> поведение меняется

        pool, token0, token1, pool_address = self.preparing(
            w3=w3,
            token0=token0,
            token1=token1
        )
        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)
        account = self.get_account(w3=w3, key=key)
        signer = account.address

        amount = self.get_amount(w3=w3, wallet=account.address)

        if amount == 0:
            return

        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        if pool_address == cst.ZERO_ADDRESS:
            return

        if token_in != 'ETH':
            amount /= 10 ** 18
            rate = self.get_rate(w3=w3, pool=pool_address, token_ch=token0)
            amount = self.get_swap_amount(amount=amount, rate=rate)

        if token_in != 'ETH':
            try:
                approved_tx = self.approve_swap(
                    w3=w3,
                    token=token0,
                    amount=amount,
                    signer=account,
                    sign_addr=signer,
                    spender=cst.ROUTER,
                )

                if approved_tx:
                    tx_rec = w3.eth.wait_for_transaction_receipt(approved_tx)
                    status = tx_rec['status']
                    print(f'Approve tx: {approved_tx.hex()}. Status: {status}')
                    time.sleep(50)
                else:
                    print("Doesn't need approve")
                    time.sleep(20)
            except Exception as err:
                print(err)

        tx = self.create_liq_tx(
            pool=pool_address,
            token_in=token_in,
            router=router,
            token0=token0,
            token1=token1,
            wallet=signer,
            amount=amount,
            w3=w3
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

    @staticmethod
    def create_liq_tx(
            router: web3.contract.Contract,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            wallet: ChecksumAddress,
            pool: ChecksumAddress,
            token_in: str,
            amount: int,
            w3: Web3,
    ) -> TxParams:
        """Функция создания транзакции добавления ликвидности"""

        inputs = [
            (token1, 0), (cst.CALLBACK, amount)
        ] if token_in == 'ETH' else [
            (token0, amount)
        ]

        txn = router.functions.addLiquidity2(
            pool,
            inputs,
            eth_abi.encode(['address'], [wallet]),
            cst.MIN_LIQ,
            cst.CALLBACK,
            '0x'
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

    @staticmethod
    def get_swap_amount(amount: float, rate: float, dec: int = 6) -> int:
        """Функция суммы для обмена USDT/USDC"""

        return int(amount * rate * (10 ** dec))

    def preparing(self, w3: Web3, token0: str, token1: str) -> [
        web3.contract.Contract,
        ChecksumAddress,
        ChecksumAddress,
        ChecksumAddress
    ]:
        """Функция предварительного получения всех необходимых данных"""

        token0 = self.to_address(token0)
        token1 = self.to_address(token1)

        pool = self.get_contract(w3=w3, address=cst.POOL_FACTORY, abi=FACTORY_ABI)
        pool_address = pool.functions.getPool(token0, token1).call()

        return [pool, token0, token1, pool_address]
