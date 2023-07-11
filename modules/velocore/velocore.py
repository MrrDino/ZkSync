import web3
import time

import constants as cst

from web3 import Web3
from web3.types import ChecksumAddress
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from abis.router import ROUTER_ABI
from modules.helper import SimpleW3


class Velocore(SimpleW3):

    def start_swap(self, key: str, token0: str, token1: str, amount: float = None) -> int or None:
        """Функция запуска tokens swap для Velocore"""

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
        """Функция выполнения обмена для Velocore"""

        token0, token1, signer, router = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )
        token_in = cst.TOKENS[token0.lower()]  # если ETH -> поведение меняется

        #  Если повторный свап -> переводим сумму из ETH в USDC
        if isinstance(amount, float):
            amount = self.get_usd_value(
                token1=token0,
                token0=token1,
                router=router,
                amount_in=amount,
            )

        if token_in == 'ETH':
            swap_tx = router.functions.swapExactETHForTokens(
                0,
                [{'from': token0, 'to': token1, 'stable': False}],
                signer,
                int(time.time()) + 1800,
            ).build_transaction({
                'gas': 0,
                'from': signer,
                'value': amount,
                'maxFeePerGas': 0,
                'maxPriorityFeePerGas': 0,
                'nonce': w3.eth.get_transaction_count(signer),
            })
        else:
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

            swap_tx = router.functions.swapExactTokensForETH(
                amount,
                0,
                [{'from': token0, 'to': token1, 'stable': False}],
                signer,
                int(time.time()) + 1800,
            ).build_transaction({
                'gas': 0,
                'value': 0,
                'from': signer,
                'maxFeePerGas': 0,
                'maxPriorityFeePerGas': 0,
                'nonce': w3.eth.get_transaction_count(signer),
            })

        swap_tx.update(
            {
                'gas': w3.eth.estimate_gas(swap_tx),
                'maxFeePerGas': w3.eth.gas_price,
                'maxPriorityFeePerGas': w3.eth.gas_price
            }
        )

        signed_tx = account.sign_transaction(transaction_dict=swap_tx)
        time.sleep(30)

        try:
            tx = w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = w3.eth.wait_for_transaction_receipt(tx)
            status = tx_rec['status']  # будет использоваться для переотправки
            print(f'Tx: {tx.hex()}. Status: {status}')

        except BaseException as err:
            print(err)

        return True

    def add_liquidity(self, token0: str, key: str):
        """Функция добавления ликвидности для Sapce Finance"""

        token1 = cst.ETH  # Почти все пулы (кроме стейблов с ETH)
        w3 = self.connect()
        account = self.get_account(w3=w3, key=key)
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        token0, token1, signer, router = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )
        amount = self.get_amount(w3=w3, wallet=signer)

        if amount == 0:  # сделать ожидание ввода нужной суммы
            return

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
                time.sleep(70)
            else:
                print("Doesn't need approve")
                time.sleep(20)
        except Exception as err:
            print(err)

        liq_tx = router.functions.addLiquidityETH(
            token0,
            True,  # Easier withdraw from stable pool
            amount,
            cst.MIN_AMOUNT,
            cst.MIN_AMOUNT,
            signer,
            int(time.time()) + 1800,
        ).build_transaction({
                'gas': 0,
                'value': amount,
                'from': signer,
                'maxFeePerGas': 0,
                'maxPriorityFeePerGas': 0,
                'nonce': w3.eth.get_transaction_count(signer),
            })

        liq_tx.update(
            {
                'gas': w3.eth.estimate_gas(liq_tx),
                'maxFeePerGas': w3.eth.gas_price,
                'maxPriorityFeePerGas': w3.eth.gas_price
            }
        )

        signed_tx = account.sign_transaction(transaction_dict=liq_tx)
        time.sleep(30)

        try:
            tx = w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = w3.eth.wait_for_transaction_receipt(tx)
            status = tx_rec['status']  # будет использоваться для переотправки
            print(f'Tx: {tx.hex()}. Status: {status}')
        except Exception as err:
            print(err)

        return True

    @staticmethod
    def get_usd_value(
            amount_in: float,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            router: web3.contract.Contract
    ) -> int:
        """Функция получения курса для пары"""

        amount_in = int(amount_in * 10 ** 18)

        amount_data = router.functions.getAmountOut(amount_in, token0, token1).call()
        amount = int(amount_data[0] * .98)

        return amount

    def prepare(
            self,
            w3: Web3,
            token0: str,
            token1: str,
            account: LocalAccount
    ) -> [
        ChecksumAddress,
        ChecksumAddress,
        ChecksumAddress,
        web3.contract.Contract
    ]:
        """Функция преобразования первичных данных"""

        token0 = self.to_address(token0)
        token1 = self.to_address(token1)
        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)

        return [token0, token1, account.address, router]
