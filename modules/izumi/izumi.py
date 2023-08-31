import json
import random
import asyncio
import aiohttp
import web3.contract

from loguru import logger
from web3 import AsyncWeb3
from web3.types import ChecksumAddress
from eth_account.signers.local import LocalAccount

from modules import settings as conf
from modules.izumi import constants as cst
from modules import global_constants as gc
from modules.izumi.abis.router import ROUTER_ABI
from modules.helper import SimpleW3, retry, get_gas, wait, write_file


class Izumi(SimpleW3):

    # @retry
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
        """Функция запуска tokens swap для Izumi"""

        w3 = await self.connect()
        account = self.get_account(w3=w3, key=key)

        if pub_key:
            logger.info(
                f"Work with \33[{35}m{account.address}\033[0m, action: {action}, exchange: \33[{36}m{exchange}\033[0m"
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
        """Функция выполнения обмена для Izumi"""

        token0, token1, signer, router = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )

        token0 = self.to_address(token0)
        token1 = self.to_address(token1)
        token_in = cst.TOKENS[token0.lower()]
        token_out = cst.TOKENS[token1.lower()]

        if isinstance(amount, float):
            amount = await self.get_usd_value(
                amount_in=amount
            )

        if token_in == 'ETH':
            min_acquired = await self.get_usd_value(
                amount_in=amount
            )
            min_acquired = int(min_acquired * .98)

            print(signer)
            print(amount)
            print(min_acquired)
            # path = to_bytes(text=cst.PATHS[token_out]['in'])
            # print(path)
            path = token0 + '0007D0' + token1[2:]
            print(path)

            data = [router.encodeABI(
                fn_name='swapAmount',
                args=[(
                    path,
                    signer,
                    amount,
                    min_acquired,
                    self.deadline()
                )]
            )]

            swap_data = data + [router.encodeABI(fn_name='refundETH', args=[])]
        else:
            min_acquired = await self.get_eth_value(
                amount_in=amount
            )
            min_acquired = int(min_acquired * .98)

            # path = to_bytes(text=cst.PATHS[token_in]['out'])
            path = token0 + '000190' + token1[:2]
            print(1, path)

            data = [router.encodeABI(
                fn_name='swapAmount',
                args=[(
                    path,
                    self.to_address('0x0000000000000000000000000000000000000000'),
                    amount,
                    min_acquired,
                    self.deadline()
                )]
            )]
            swap_data = data + [router.encodeABI(fn_name='unwrapWETH9', args=[0, signer])]

        status = 0
        print(swap_data)
        tx = await router.functions.multicall(
            swap_data
        ).build_transaction({
            'gas': 0,
            'value': 0 if token_in != 'ETH' else amount,
            'from': signer,
            'maxFeePerGas': 0,
            'maxPriorityFeePerGas': 0,
            'nonce': await w3.eth.get_transaction_count(signer),
        })

        gas_price = await w3.eth.gas_price
        tx['maxFeePerGas'] = int(gas_price * 1.1)
        tx['maxPriorityFeePerGas'] = gas_price
        tx['gas'] = await w3.eth.estimate_gas(tx)

        delay = random.randint(gc.BUILD_DELAY[0], gc.BUILD_DELAY[1])
        logger.info("Transaction built")
        await wait(_time=delay)

        signed_tx = account.sign_transaction(tx)

        delay = random.randint(gc.SIGN_DELAY[0], gc.SIGN_DELAY[1])
        logger.info("Transaction signed")
        await wait(_time=delay)

        try:

            swap_tx = await w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)

            delay = random.randint(gc.SIGN_DELAY[0], gc.SIGN_DELAY[1])
            logger.info("Transaction sent")
            await wait(_time=delay)

            tx_rec = await w3.eth.wait_for_transaction_receipt(swap_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = await self.get_fee_by_url(gas_price=gas_price, gas_used=tx_rec['gasUsed'])
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

        if token_in == 'ETH':
            return amount

    # @retry
    async def add_liquidity(self, token0: str, key: str, exchange: str, mode: int = 1):
        """Функция добавления ликвидности для Izumi"""

        amount = None
        w3 = await self.connect()
        token1 = self.to_address(gc.ETH)
        account = self.get_account(w3=w3, key=key)

        logger.info(
            f"Work with \33[{35}m{account.address}\033[0m, action: add liq, exchange: \33[{36}m{exchange}\033[0m"
        )

        token0, token1, signer, router = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )

        eth = await self.get_eth_price()
        token0 = self.to_address(token0)
        token1 = self.to_address(token1)
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

        await self.approve(
            w3=w3,
            token=token0,
            signer=signer,
            amount=amount,
            account=account,
            spender=self.to_address(cst.ROUTER)
        )

        liq_data = router.encodeABI(
            fn_name="mint",
            args=[(

            )]
        )

    async def approve(
            self,
            amount: int,
            w3: AsyncWeb3,
            account: LocalAccount,
            token: ChecksumAddress,
            signer: ChecksumAddress,
            spender: ChecksumAddress,
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

                fee = await self.get_fee_by_url(
                    gas_used=tx_rec['gasUsed'],
                    gas_price=gas_price,
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

    async def get_usd_value(self, amount_in: float) -> int:
        """Функция преобразования суммы ETH в USDC"""

        eth_price = await self.get_eth_price()
        usdc = round((amount_in * eth_price), 6)
        value = int(usdc * 10 ** cst.DECIMALS['USDC'])

        return value

    async def get_eth_value(self, amount_in: float) -> int:
        """Функция преобразования суммы USDC в ETH"""

        eth_price = await self.get_eth_price()
        value = int(amount_in / eth_price * 10 ** cst.DECIMALS['ETH'])

        return value

    @staticmethod
    async def get_eth_price() -> float:

        params = {
            't': ['ETH'],
        }

        price = None

        async with aiohttp.ClientSession() as session:

            while not price:
                try:
                    response = await session.get(
                        'https://api.izumi.finance/api/v1/token_info/price_info/',
                        params=params,
                        headers=cst.HEADERS
                    )
                    if response.status == 200:
                        price = json.loads(await response.text())['data']

                except Exception as err:
                    logger.error(err)
                    await asyncio.sleep(1.5)

        return  price['ETH']