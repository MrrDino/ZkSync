import web3
import time

import global_constants as gc

from web3 import Web3
from loguru import logger
from web3.types import ChecksumAddress
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from . import constants as cst
from .abis.pair import PAIR_ABI
from .abis.router import ROUTER_ABI
from .abis.factory import FACTORY_ABI
from helper import SimpleW3, retry, get_gas


class MuteIO(SimpleW3):

    @retry
    def start_swap(
            self,
            key: str,
            token0: str,
            token1: str,
            mode: int = 0,
            amount: float = None,
            exchange: str = None,
            pub_key: bool = False
    ) -> int or bool:
        """Функция запуска tokens swap для Mute.io"""

        w3 = self.connect()
        account = self.get_account(w3=w3, key=key)
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        if pub_key:
            logger.info(f"Work with \33[{35}m{account.address}\033[0m Exchange: \33[{36}m{exchange}\033[0m")

        if not amount:
            need_msg = True

            while not amount:
                amount = self.get_amount(w3=w3, wallet=account.address, mode=mode)

                if not amount:
                    if need_msg:
                        logger.error(f"Insufficient balance! Address - {account.address} key - {key}")
                        need_msg = False
                    time.sleep(gc.TOP_UP_WAIT)

            router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)

            liq_check = self.get_price_impact(
                w3=w3,
                amount=amount,
                router=router,
                token0=self.to_address(token0),
                token1=self.to_address(token1)
            )

            if not liq_check:
                return False

            self.make_swap(w3=w3, amount=amount, account=account, token0=token0, token1=token1)
            return amount
        else:
            self.make_swap(w3=w3, amount=amount, account=account, token0=token0, token1=token1)

    def make_swap(
            self,
            w3: Web3,
            token0: str,
            token1: str,
            amount: int or float,
            account: LocalAccount,
    ):
        """Функция выполнения обмена для Mute.io"""

        token0, token1, signer, router = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )
        token_in = cst.TOKENS[token0.lower()]  # если ETH -> поведение меняется
        token_out = cst.TOKENS[token1.lower()]

        #  Если повторный свап -> переводим сумму из ETH в USDC
        if isinstance(amount, float):
            amount = self.get_usd_value(
                token_in=token_in,
                amount=amount,
                router=router,
                token0=token1,
                token1=token0
            )

        if token_in == 'ETH':
            swap_tx = router.functions.swapExactETHForTokens(
                0,
                [token0, token1],
                signer,
                self.deadline(),
                [False, False]
            ).build_transaction({
                'gas': 0,
                'from': signer,
                'value': amount,
                'maxFeePerGas': 0,
                'maxPriorityFeePerGas': 0,
                'nonce': w3.eth.get_transaction_count(signer),
            })
        else:
            self.approve(
                w3=w3,
                token=token0,
                signer=signer,
                amount=amount,
                router=router,
                account=account,
                token_in=token_in,
                spender=self.to_address(cst.ROUTER)
            )

            swap_tx = router.functions.swapExactTokensForETH(
                amount,
                0,
                [token0, token1],
                signer,
                self.deadline(),
                [False, False]
            ).build_transaction({
                'gas': 0,
                'value': 0,
                'from': signer,
                'maxFeePerGas': 0,
                'maxPriorityFeePerGas': 0,
                'nonce': w3.eth.get_transaction_count(signer),
            })

        gas_price = w3.eth.gas_price
        swap_tx['maxFeePerGas'] = int(gas_price * 1.1)
        swap_tx['maxPriorityFeePerGas'] = gas_price
        swap_tx['gas'] = w3.eth.estimate_gas(swap_tx)

        signed_tx = account.sign_transaction(transaction_dict=swap_tx)
        logger.info("Swap transaction signed. Wait 30 sec.")
        time.sleep(30)
        status = 0

        try:
            swap_tx = w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = w3.eth.wait_for_transaction_receipt(swap_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = self.get_fee(
                gas_used=tx_rec['gasUsed'],
                gas_price=gas_price,
                token_in=token_in,
                router=router
            )
            tx_fee = f"tx fee ${fee}"

            logger.info(
                f'||SWAP to {token_out}| https://www.okx.com/explorer/zksync/tx/{swap_tx.hex()} '
                f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
            )
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

        assert status == 1  # если статус != 1 транзакция не прошла

    @retry
    def add_liquidity(self, token0: str, key: str, mode: int = 1) -> bool:
        """Функция добавления ликвидности для Mute.io"""

        amount = None
        w3 = self.connect()
        token1 = self.to_address(gc.ETH)
        account = self.get_account(w3=w3, key=key)
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        token0, token1, signer, router = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )
        factory = self.get_contract(w3=w3, address=cst.FACTORY, abi=FACTORY_ABI)
        pair_address = factory.functions.getPair(
            self.to_address(gc.ETH),
            self.to_address(gc.USDC),
            False
        ).call()

        eth = self.get_eth(w3=w3, abi=PAIR_ABI, pair_address=pair_address)

        token_in = cst.TOKENS[token0.lower()]
        token_out = cst.TOKENS[token1.lower()]

        if not amount:
            need_msg = True

            while not amount:
                amount = self.get_amount(w3=w3, wallet=account.address, mode=mode, eth=eth)

                if not amount:
                    if need_msg:
                        logger.error(f"Insufficient balance! Address - {account.address} key - {key}")
                        need_msg = False
                    time.sleep(gc.TOP_UP_WAIT)

        balance_check = self.check_amount(
            w3=w3,
            eth=amount,
            token=token0,
            wallet=signer,
            p_abi=PAIR_ABI,
            f_abi=FACTORY_ABI,
            f_address=cst.FACTORY
        )

        if not balance_check:
            logger.info(f"Insufficient balance of token \33[{36}m{token0}\033[0m")
            return False

        self.approve(
            w3=w3,
            token=token0,
            signer=signer,
            amount=amount,
            router=router,
            account=account,
            token_in=token_in,
            spender=self.to_address(cst.ROUTER)
        )

        # eth_min = int(amount * 0.99)  #   transferFrom failed - возможно не работает из-за проскльзывания

        liq_tx = router.functions.addLiquidityETH(
            token0,
            amount,
            cst.MIN_AMOUNT,
            cst.MIN_AMOUNT,
            signer,
            self.deadline(),
            cst.FEES[token0.lower()],
            False
        ).build_transaction({
                'gas': 0,
                'value': amount,
                'from': signer,
                'maxFeePerGas': 0,
                'maxPriorityFeePerGas': 0,
                'nonce': w3.eth.get_transaction_count(signer),
        })

        gas_price = w3.eth.gas_price
        liq_tx['maxFeePerGas'] = int(gas_price * 1.1)
        liq_tx['maxPriorityFeePerGas'] = gas_price
        liq_tx['gas'] = w3.eth.estimate_gas(liq_tx)

        signed_tx = account.sign_transaction(transaction_dict=liq_tx)
        logger.info("Liquidity transaction signed. Wait 30 sec.")
        time.sleep(30)
        status = 0

        try:
            liq_tx = w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = w3.eth.wait_for_transaction_receipt(liq_tx)
            gas = get_gas()
            status = tx_rec['status']
            fee = self.get_fee(
                gas_used=tx_rec['gasUsed'],
                gas_price=gas_price,
                token_in=token_in,
                router=router
            )
            tx_fee = f"tx fee ${fee}"

            logger.info(
                f'||ADD LIQ {token_in}/{token_out}| https://www.okx.com/explorer/zksync/tx/{liq_tx.hex()} '
                f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
            )
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

        assert status == 1  # если статус != 1 транзакция не прошла

    def approve(
            self,
            w3: Web3,
            amount: int,
            token_in: str,
            account: LocalAccount,
            token: ChecksumAddress,
            signer: ChecksumAddress,
            spender: ChecksumAddress,
            router: web3.contract.Contract
    ):
        """Функция подтверждения использования средств"""
        try:
            approved_tx = self.approve_swap(
                w3=w3,
                token=token,
                amount=amount,
                signer=account,
                sign_addr=signer,
                spender=spender,
            )

            if approved_tx:
                gas = get_gas()
                gas_price = w3.eth.gas_price

                tx_rec = w3.eth.wait_for_transaction_receipt(approved_tx)

                fee = self.get_fee(
                    gas_used=tx_rec['gasUsed'],
                    gas_price=gas_price,
                    token_in=token_in,
                    router=router
                )
                tx_fee = f"tx fee ${fee}"

                logger.info(
                    f'||APPROVE| https://www.okx.com/explorer/zksync/tx/{approved_tx.hex()} '
                    f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
                )
                logger.info('Wait 30 sec.')

                time.sleep(30)
            else:
                logger.info("Doesn't need approve. Wait 10 sec.")
                time.sleep(10)
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

    @staticmethod
    def get_usd_value(
            amount: float,
            token_in: str,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            router: web3.contract.Contract,
            liq: bool = False  # На больших суммах большое изменение цены
    ) -> int:
        """Функция получения курса для пары"""

        amount = int(amount * 10 ** 18)
        quote_info = router.functions.getAmountOut(amount, token0, token1).call()

        if token_in == 'USD':
            quote = int((quote_info[0] * .98))
        else:
            quote = quote_info[0]
        if liq:
            quote = quote * 100 / quote_info[2]

        return quote

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

    def get_fee(
            self,
            token_in: str,
            gas_price: int,
            gas_used: float,
            router: web3.contract.Contract
    ) -> float:
        """Функция получения комиссии транзакции в долларах"""

        amount = (gas_used * gas_price) / 10 ** 18
        token0 = self.to_address('0x5aea5775959fbc2557cc8789bc1bf90a239d9a91')
        token1 = self.to_address('0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4')
        fee = self.get_usd_value(amount=amount, router=router, token0=token0, token1=token1, token_in=token_in)

        return round((fee / 10 ** 6), 2)

    def get_price_impact(
            self,
            w3: Web3,
            amount: int,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            router: web3.contract.Contract,
            stable: bool = False,
    ) -> bool:
        """Функция получения изменения цены"""

        # stable pool (x^3 * y) + (y^3 * x) >= k
        # normal pool x * y >= k  <- our choice

        pool_name = f'{cst.TOKENS[token0.lower()]}/{cst.TOKENS[token1.lower()]}'
        token0_res, token1_res, tkn0, decs0, decs1 = self.get_reserves(
            w3=w3,
            stable=stable,
            token0=token0,
            token1=token1,
            p_abi=PAIR_ABI,
            f_abi=FACTORY_ABI,
            f_address=cst.FACTORY
        )

        amount /= 10 ** decs0

        if tkn0.lower() == gc.ETH.lower():
            liquidity = self.get_usd_value(
                amount=token0_res,
                token_in='ETH',
                token0=self.to_address(gc.ETH),
                token1=self.to_address(gc.USDC),
                router=router,
                liq=True
            ) * 2 / 10 ** 6
        else:
            liquidity = self.get_usd_value(
                amount=token1_res,
                token_in='ETH',
                token0=self.to_address(gc.ETH),
                token1=self.to_address(gc.USDC),
                router=router,
                liq=True
            ) * 2 / 10 ** 6

        if liquidity < gc.MIN_LIQUIDITY:
            logger.info(f"Pool \33[{35}m{pool_name}\033[0m low liquidity - {round(liquidity, 2)}$")
            return False

        k = token0_res * token1_res  # constant product

        new_token0_res = token0_res + amount
        new_token1_res = k / new_token0_res

        old_price = token0_res / token1_res
        new_price = new_token0_res / new_token1_res

        price_impact = new_price * 100 / old_price - 100

        if price_impact > gc.MAX_PRICE_IMPACT:
            logger.info(
                f"Pool \33[{35}m{pool_name}\033[0m high price impact - {round(price_impact, 5)}%"
            )
            return False

        return True
