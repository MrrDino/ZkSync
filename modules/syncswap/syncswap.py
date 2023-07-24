import web3
import eth_abi
import asyncio

import global_constants as gc

from loguru import logger
from web3 import AsyncWeb3
from web3.types import TxParams, ChecksumAddress
from eth_account.signers.local import LocalAccount

from . import constants as cst
from .abis.pool import POOL_ABI
from .abis.router import ROUTER_ABI
from .abis.factory import FACTORY_ABI
from helper import SimpleW3, retry, get_gas


class SyncSwap(SimpleW3):

    @retry
    async def start_swap(
            self,
            key: str,
            token0: str,
            token1: str,
            mode: int = 0,
            amount: float = None,
            exchange: str = None,
            pub_key: bool = False,
            shit_coin: bool = False
    ) -> int or bool:
        """Функция запуска tokens swap для SyncSwap"""

        w3 = await self.connect()
        account = self.get_account(w3=w3, key=key)

        if pub_key:
            logger.info(f"Work with \33[{35}m{account.address}\033[0m Exchange: \33[{36}m{exchange}\033[0m")

        if not amount:
            need_msg = True

            while not amount:
                amount = await self.get_amount(w3=w3, wallet=account.address, mode=mode)

                if not amount:
                    if need_msg:
                        logger.error(f"Insufficient balance! Address - {account.address} key - {key}.")
                        need_msg = False
                    await asyncio.sleep(gc.TOP_UP_WAIT)

            if not shit_coin:
                liq_check = await self.get_price_impact(
                    w3=w3,
                    amount=amount,
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
            account: LocalAccount
    ):
        """Функция выполнения обмена для SyncSwap"""

        pool, token0, token1, pool_address, signer = await self.preparing(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )
        token_in = cst.TOKENS[token0.lower()]  # если ETH -> поведение меняется
        token_out = cst.TOKENS[token1.lower()]

        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)

        #  Если повторный свап -> переводим сумму из ETH в USDC
        if isinstance(amount, float):
            amount = await self.get_usd_value(w3=w3, amount=amount, token_ch=token0)

        if token_in != 'ETH':
            await self.approve(
                w3=w3,
                token=token0,
                signer=signer,
                amount=amount,
                account=account,
                spender=cst.ROUTER
            )

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

        swap_tx = await self.create_swap_tx(
            w3=w3,
            paths=paths,
            wallet=signer,
            router=router,
            amount=amount,
            token_in=token_in
        )

        gas_price = await w3.eth.gas_price
        swap_tx['maxFeePerGas'] = int(gas_price * 1.1)
        swap_tx['maxPriorityFeePerGas'] = gas_price
        swap_tx['gas'] = await w3.eth.estimate_gas(swap_tx)

        signed_tx = account.sign_transaction(transaction_dict=swap_tx)
        logger.info("Swap transaction signed. Wait 20 sec.")
        await asyncio.sleep(20)

        status = 0

        try:
            swap_tx = await w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = await w3.eth.wait_for_transaction_receipt(swap_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = await self.get_fee(
                w3=w3,
                gas_price=gas_price,
                gas_used=tx_rec['gasUsed']
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
    async def add_liquidity(
            self,
            key: str,
            token1: str,
            mode: int = 1
    ):
        """Функция добавления ликвидности для SyncSwap"""

        amount = None
        w3 = await self.connect()
        token0 = self.to_address(gc.ETH)
        account = self.get_account(w3=w3, key=key)
        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)

        pool, token0, token1, pool_address, signer = await self.preparing(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )

        pair_address = await pool.functions.getPool(
            self.to_address(gc.ETH),
            self.to_address(gc.USDC)
        ).call()
        eth = await self.get_eth(w3=w3, abi=POOL_ABI, pair_address=pair_address)

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
                    await asyncio.sleep(gc.TOP_UP_WAIT)

        if token_in != 'ETH':
            amount = await self.get_usd_value(w3=w3, amount=amount, token_ch=token0)

            await self.approve(
                w3=w3,
                token=token0,
                signer=signer,
                amount=amount,
                account=account,
                spender=cst.ROUTER
            )

        liq_tx = await self.create_liq_tx(
            pool=pool_address,
            token_in=token_in,
            router=router,
            token0=token0,
            token1=token1,
            wallet=signer,
            amount=amount,
            w3=w3
        )

        gas_price = await w3.eth.gas_price
        liq_tx['maxFeePerGas'] = int(gas_price * 1.1)
        liq_tx['maxPriorityFeePerGas'] = gas_price
        liq_tx['gas'] = await w3.eth.estimate_gas(liq_tx)

        signed_tx = account.sign_transaction(transaction_dict=liq_tx)
        logger.info("Liquidity transaction signed. Wait 20 sec.")
        await asyncio.sleep(20)

        status = 0

        try:
            liq_tx = await w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = await w3.eth.wait_for_transaction_receipt(liq_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = await self.get_fee(
                w3=w3,
                gas_price=gas_price,
                gas_used=tx_rec['gasUsed']
            )
            tx_fee = f"tx fee ${fee}"

            logger.info(
                f'||ADD LIQ {token_in}/{token_out}| https://www.okx.com/explorer/zksync/tx/{liq_tx.hex()} '
                f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
            )
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

        assert status == 1  # если статус != 1 транзакция не прошла

    async def preparing(self, w3: AsyncWeb3, token0: str, token1: str, account: LocalAccount) -> [
        web3.contract.Contract,
        LocalAccount,
        ChecksumAddress,
        ChecksumAddress,
        ChecksumAddress,
        ChecksumAddress
    ]:
        """Функция предварительного получения всех необходимых данных"""

        token0 = self.to_address(token0)
        token1 = self.to_address(token1)

        pool = self.get_contract(w3=w3, address=cst.FACTORY, abi=FACTORY_ABI)
        pool_address = await pool.functions.getPool(token0, token1).call()

        return [pool, token0, token1, pool_address, account.address]

    @staticmethod
    async def create_liq_tx(
            amount: int,
            token_in: str,
            w3: AsyncWeb3,
            pool: ChecksumAddress,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            wallet: ChecksumAddress,
            router: web3.contract.Contract,
    ) -> TxParams:
        """Функция создания транзакции добавления ликвидности"""

        inputs = [
            (token1, 0), (cst.ZERO_ADDRESS, amount)
        ] if token_in == 'ETH' else [
            (token0, amount)
        ]

        txn = await router.functions.addLiquidity2(
            pool,
            inputs,
            eth_abi.encode(['address'], [wallet]),
            cst.MIN_LIQ,
            cst.ZERO_ADDRESS,
            '0x'
        ).build_transaction({
            'gas': 0,
            'from': wallet,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'value': amount if token_in == 'ETH' else 0,
            'nonce': await w3.eth.get_transaction_count(wallet),
        })

        return txn

    async def create_swap_tx(
            self,
            paths: list,
            amount: int,
            w3: AsyncWeb3,
            token_in: str,
            wallet: ChecksumAddress,
            router: web3.contract.Contract,
    ) -> TxParams:

        txn = await router.functions.swap(
            paths,
            0,
            self.deadline(),
        ).build_transaction({
            'gas': 0,
            'from': wallet,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'value': amount if token_in == 'ETH' else 0,
            'nonce': await w3.eth.get_transaction_count(wallet),
        })

        return txn

    async def get_usd_value(
            self,
            w3: AsyncWeb3,
            amount: float,
            token_ch: ChecksumAddress,
    ) -> int:
        """Функция получения курса в пуле"""

        token0_res, token1_res, tkn0, decs0, decs1 = await self.get_reserves(
            w3=w3,
            stable=False,  # parameter is unnecessary
            p_abi=POOL_ABI,
            f_abi=FACTORY_ABI,
            exchange='SyncSwap',
            f_address=cst.FACTORY,
            token0=self.to_address(gc.USDC),
            token1=self.to_address(gc.ETH),
        )

        if cst.TOKENS[tkn0.lower()] == 'ETH':
            usd = int(token1_res / token1_res)
        else:
            usd = int(token0_res / token1_res)

        usd -= usd * cst.MULTS[token_ch.lower()]

        return int(amount * usd * (10 ** decs0))

    async def get_fee(
            self,
            w3: AsyncWeb3,
            gas_price: int,
            gas_used: float,
    ) -> float:
        """Функция получения комиссии транзакции в долларах"""

        amount = (gas_used * gas_price) / 10 ** 18
        token1 = self.to_address(gc.USDC)
        fee = await self.get_usd_value(w3=w3, amount=amount, token_ch=token1)

        return round((fee / 10 ** 6), 2)

    async def approve(
            self,
            amount: int,
            w3: AsyncWeb3,
            account: LocalAccount,
            token: ChecksumAddress,
            signer: ChecksumAddress,
            spender: ChecksumAddress
    ):
        """Функция подтверждения использования средств"""

        try:
            approved_tx = await self.approve_swap(
                w3=w3,
                token=token,
                amount=amount,
                signer=account,
                spender=spender,
                sign_addr=signer
            )

            if approved_tx:
                gas = get_gas()
                gas_price = await w3.eth.gas_price

                tx_rec = await w3.eth.wait_for_transaction_receipt(approved_tx)

                fee = await self.get_fee(
                    w3=w3,
                    gas_price=gas_price,
                    gas_used=tx_rec['gasUsed']
                )
                tx_fee = f"tx fee ${fee}"

                logger.info(
                    f'||APPROVE| https://www.okx.com/explorer/zksync/tx/{approved_tx.hex()} '
                    f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
                )
                logger.info('Wait 30 sec.')

                await asyncio.sleep(40)
            else:
                logger.info("Doesn't need approve. Wait 5 sec.")
                await asyncio.sleep(10)
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

    async def get_price_impact(
            self,
            amount: int,
            w3: AsyncWeb3,
            token0: ChecksumAddress,
            token1: ChecksumAddress,
            stable: bool = False,
    ) -> float:
        """Функция получения изменения цены"""

        # classic pool k = x * y <- our choice
        # stable pool k = x + y

        pool_name = f'{cst.TOKENS[token0.lower()]}/{cst.TOKENS[token1.lower()]}'
        token0_res, token1_res, tkn0, decs0, decs1 = await self.get_reserves(
            w3=w3,
            stable=stable,
            token0=token0,
            token1=token1,
            p_abi=POOL_ABI,
            f_abi=FACTORY_ABI,
            exchange='SyncSwap',
            f_address=cst.FACTORY
        )

        amount /= 10 ** decs0

        if tkn0.lower() == gc.ETH.lower():
            liquidity = await self.get_usd_value(
                w3=w3,
                amount=token0_res,
                token_ch=self.to_address(gc.USDC)
            ) * 2 / 10 ** 6
        else:
            liquidity = await self.get_usd_value(
                w3=w3,
                amount=token1_res,
                token_ch=self.to_address(gc.USDC)
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
