import web3
import random

import settings as conf
import global_constants as gc

from loguru import logger
from web3 import AsyncWeb3
from web3.types import ChecksumAddress
from eth_account.signers.local import LocalAccount

from mute import constants as cst
from mute.abis.pair import PAIR_ABI
from mute.abis.router import ROUTER_ABI
from mute.abis.factory import FACTORY_ABI
from helper import SimpleW3, retry, get_gas, wait, write_file


class MuteIO(SimpleW3):

    @retry
    async def start_swap(
            self,
            key: str,
            token0: str,
            token1: str,
            mode: int = 0,
            action: str = None,
            amount: float = None,
            exchange: str = None,
            pub_key: bool = False
    ) -> int or bool:
        """Функция запуска tokens swap для Mute.io"""

        w3 = await self.connect()
        account = self.get_account(w3=w3, key=key)

        if pub_key:
            logger.info(
                f"Action: {action}, exchange: \33[{36}m{exchange}\033[0m"
            )

        if not amount:
            need_msg = True

            while not amount:
                amount = await self.get_amount(w3=w3, wallet=account.address, mode=mode)

                if not amount:
                    if need_msg:
                        logger.error(f"Insufficient balance! Address - {account.address} key - {key}")
                        need_msg = False
                    await wait(_time=conf.TOP_UP_WAIT)

            router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)

            liq_check = await self.get_price_impact(
                w3=w3,
                amount=amount,
                router=router,
                token0=self.to_address(token0),
                token1=self.to_address(token1)
            )

            if not liq_check:
                return False

            await self.make_swap(w3=w3, amount=amount, account=account, token0=token0, token1=token1)
            return amount
        else:
            await self.make_swap(w3=w3, amount=amount, account=account, token0=token0, token1=token1)

    async def make_swap(
            self,
            token0: str,
            token1: str,
            w3: AsyncWeb3,
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
            amount = await self.get_usd_value(
                token_in=token_in,
                amount=amount,
                router=router,
                token0=token1,
                token1=token0
            )

        if token_in == 'ETH':
            swap_tx = await router.functions.swapExactETHForTokens(
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
                'nonce': await w3.eth.get_transaction_count(signer),
            })
        else:
            await self.approve(
                w3=w3,
                token=token0,
                signer=signer,
                amount=amount,
                router=router,
                account=account,
                token_in=token_in,
                spender=self.to_address(cst.ROUTER)
            )

            swap_tx = await router.functions.swapExactTokensForETH(
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
                'nonce': await w3.eth.get_transaction_count(signer),
            })

        gas_price = await w3.eth.gas_price
        swap_tx['maxFeePerGas'] = int(gas_price * 1.1)
        swap_tx['maxPriorityFeePerGas'] = gas_price
        swap_tx['gas'] = await w3.eth.estimate_gas(swap_tx)

        signed_tx = account.sign_transaction(transaction_dict=swap_tx)

        delay = random.randint(gc.SIGN_DELAY[0], gc.SIGN_DELAY[1])
        logger.info("Transaction signed")
        await wait(_time=delay)

        status = 0

        try:
            swap_tx = await w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)

            delay = random.randint(gc.SIGN_DELAY[0], gc.SIGN_DELAY[1])
            logger.info("Transaction sent")
            await wait(_time=delay)

            tx_rec = await w3.eth.wait_for_transaction_receipt(swap_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = await self.get_fee(
                gas_used=tx_rec['gasUsed'],
                gas_price=gas_price,
                token_in=token_in,
                router=router
            )
            tx_fee = f"tx fee ${fee}"
            link = f"https://www.okx.com/explorer/zksync/tx/{swap_tx.hex()}"
            write_file(wallet=signer, tx=link, action=0, status=status)

            logger.info(
                f'||SWAP to {token_out}| {link} '
                f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
            )
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

        assert status == 1  # если статус != 1 транзакция не прошла

    @retry
    async def add_liquidity(self, token0: str, key: str, exchange: str, mode: int = 1) -> bool:
        """Функция добавления ликвидности для Mute.io"""

        amount = None
        w3 = await self.connect()
        token1 = self.to_address(gc.ETH)
        account = self.get_account(w3=w3, key=key)

        logger.info(
            f"Action: add add liquidity, exchange: \33[{36}m{exchange}\033[0m"
        )

        token0, token1, signer, router = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )

        factory = self.get_contract(w3=w3, address=cst.FACTORY, abi=FACTORY_ABI)
        pair_address = await factory.functions.getPair(
            self.to_address(gc.ETH),
            self.to_address(gc.USDC),
            False
        ).call()

        eth = await self.get_eth(w3=w3, abi=PAIR_ABI, pair_address=pair_address)

        token_in = cst.TOKENS[token0.lower()]
        token_out = cst.TOKENS[token1.lower()]

        if not amount:
            need_msg = True

            while not amount:
                amount = await self.get_amount(w3=w3, wallet=account.address, mode=mode, eth=eth)

                if not amount:
                    if need_msg:
                        logger.error(f"Insufficient balance! Address - {account.address} key - {key}")
                        need_msg = False
                    await wait(_time=conf.TOP_UP_WAIT)

        await self.make_swap(
            w3=w3,
            token0=gc.ETH,
            token1=token0,
            account=account,
            amount=amount,
        )

        await self.approve(
            w3=w3,
            token=token0,
            signer=signer,
            amount=amount,
            router=router,
            account=account,
            token_in=token_in,
            spender=self.to_address(cst.ROUTER)
        )

        liq_tx = await router.functions.addLiquidityETH(
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
                'nonce': await w3.eth.get_transaction_count(signer),
        })

        gas_price = await w3.eth.gas_price
        liq_tx['maxFeePerGas'] = int(gas_price * 1.1)
        liq_tx['maxPriorityFeePerGas'] = gas_price
        liq_tx['gas'] = await w3.eth.estimate_gas(liq_tx)

        delay = random.randint(gc.BUILD_DELAY[0], gc.BUILD_DELAY[1])
        logger.info("Transaction built")
        await wait(_time=delay)

        signed_tx = account.sign_transaction(transaction_dict=liq_tx)

        delay = random.randint(gc.SIGN_DELAY[0], gc.SIGN_DELAY[1])
        logger.info("Transaction signed")
        await wait(_time=delay)

        status = 0

        try:
            liq_tx = await w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)

            delay = random.randint(gc.SIGN_DELAY[0], gc.SIGN_DELAY[1])
            logger.info("Transaction sent")
            await wait(_time=delay)

            tx_rec = await w3.eth.wait_for_transaction_receipt(liq_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = await self.get_fee(
                gas_used=tx_rec['gasUsed'],
                gas_price=gas_price,
                token_in=token_in,
                router=router
            )
            tx_fee = f"tx fee ${fee}"
            link = f"https://www.okx.com/explorer/zksync/tx/{liq_tx.hex()}"
            write_file(wallet=signer, tx=link, action=2, status=status)

            logger.info(
                f'||ADD LIQ {token_in}/{token_out}| {link} '
                f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
            )
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

        assert status == 1  # если статус != 1 транзакция не прошла
        return True

    async def approve(
            self,
            amount: int,
            token_in: str,
            w3: AsyncWeb3,
            account: LocalAccount,
            token: ChecksumAddress,
            signer: ChecksumAddress,
            spender: ChecksumAddress,
            router: web3.contract.Contract
    ):
        """Функция подтверждения использования средств"""
        try:
            approved_tx = await self.approve_swap(
                w3=w3,
                token=token,
                amount=amount,
                signer=account,
                sign_addr=signer,
                spender=spender,
            )

            if approved_tx:
                gas = get_gas()
                gas_price = await w3.eth.gas_price

                tx_rec = await w3.eth.wait_for_transaction_receipt(approved_tx)

                fee = await self.get_fee(
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

                await wait(_time=30)
            else:
                logger.info("Doesn't need approve.")
                await wait(_time=5)
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

    @staticmethod
    async def get_usd_value(
            amount: float,
            token_in: str,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            router: web3.contract.Contract,
            liq: bool = False  # На больших суммах большое изменение цены
    ) -> int:
        """Функция получения курса для пары"""

        amount = int(amount * 10 ** 18)
        quote_info = await router.functions.getAmountOut(amount, token0, token1).call()

        if token_in == 'USD':
            quote = int((quote_info[0] * .98))
        else:
            quote = quote_info[0]
        if liq:
            quote = quote * 100 / quote_info[2]

        return quote

    def prepare(
            self,
            token0: str,
            token1: str,
            w3: AsyncWeb3,
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

    async def get_fee(
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
        fee = await self.get_usd_value(amount=amount, router=router, token0=token0, token1=token1, token_in=token_in)

        return round((fee / 10 ** 6), 2)

    async def get_price_impact(
            self,
            amount: int,
            w3: AsyncWeb3,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            router: web3.contract.Contract,
            stable: bool = False,
    ) -> bool:
        """Функция получения изменения цены"""

        # stable pool (x^3 * y) + (y^3 * x) >= k
        # normal pool x * y >= k  <- our choice

        pool_name = f'{cst.TOKENS[token0.lower()]}/{cst.TOKENS[token1.lower()]}'
        token0_res, token1_res, tkn0, decs0, decs1 = await self.get_reserves(
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
            liquidity = await self.get_usd_value(
                amount=token0_res,
                token_in='ETH',
                token0=self.to_address(gc.ETH),
                token1=self.to_address(gc.USDC),
                router=router,
                liq=True
            ) * 2 / 10 ** 6
        else:
            liquidity = await self.get_usd_value(
                amount=token1_res,
                token_in='ETH',
                token0=self.to_address(gc.ETH),
                token1=self.to_address(gc.USDC),
                router=router,
                liq=True
            ) * 2 / 10 ** 6

        if liquidity < conf.MIN_LIQUIDITY:
            logger.info(f"Pool \33[{35}m{pool_name}\033[0m low liquidity - {round(liquidity, 2)}$")
            return False

        k = token0_res * token1_res  # constant product

        new_token0_res = token0_res + amount
        new_token1_res = k / new_token0_res

        old_price = token0_res / token1_res
        new_price = new_token0_res / new_token1_res

        price_impact = new_price * 100 / old_price - 100

        if price_impact > conf.MAX_PRICE_IMPACT:
            logger.info(
                f"Pool \33[{35}m{pool_name}\033[0m high price impact - {round(price_impact, 5)}%"
            )
            return False

        return True
