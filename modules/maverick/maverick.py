import time
import random
import aiohttp

from loguru import logger
from web3 import AsyncWeb3
from web3.types import ChecksumAddress
from eth_account.signers.local import LocalAccount

import settings as conf
import global_constants as gc

from maverick import constants as cst
from maverick.abis.router import ROUTER_ABI
from helper import SimpleW3, retry, get_gas, wait, write_file


class Maverick(SimpleW3):

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
    ):
        """Функция выполнения обмена для Maverick"""

        status = 0
        w3 = await self.connect()
        account = self.get_account(w3=w3, key=key)

        if pub_key:
            logger.info(
                f"Action: {action}, exchange: \33[{36}m{exchange}\033[0m"
            )

        signer = account.address
        token0 = self.to_address(token0)
        token1 = self.to_address(token1)
        token_in = cst.TOKENS[token0.lower()]
        token_out = cst.TOKENS[token1.lower()]
        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)
        pool_address = self.generate_pool(token0=token_in, token1=token_out)
        path = f'{token0.lower()}{pool_address.lower()[2:]}{token1.lower()[2:]}'

        quote = await self.get_price(token0=token0, token1=token1)

        if not amount:
            need_msg = True

            while not amount:
                amount = await self.get_amount(w3=w3, wallet=account.address, mode=mode)

                if not amount:
                    if need_msg:
                        logger.error(f"Insufficient balance! Address - {account.address} key - {key}")
                        need_msg = False
                    await wait(_time=conf.TOP_UP_WAIT)

            min_amount = int((quote * (amount / 10 ** cst.DECIMALS[token0.lower()])) * cst.SLIPPAGE * 10 ** cst.DECIMALS[token1.lower()])
        else:
            min_amount = int((amount - amount * cst.SLIPPAGE) * 10 ** 18)  # HARDCODE DECS ETH
            amount = int((amount * quote) * 10 ** cst.DECIMALS[token0.lower()])

        if token_in != 'ETH':
            await self.approve(
                w3=w3,
                token=token0,
                signer=signer,
                amount=amount,
                account=account,
                spender=cst.ROUTER
            )

            data = [router.encodeABI(
                fn_name="exactInput",
                args=[(
                    path,
                    '0x0000000000000000000000000000000000000000',
                    self.deadline(),
                    amount,
                    min_amount
                )]
            )]
            swap_data = data + [router.encodeABI(fn_name='unwrapWETH9', args=[0, signer])]
        else:
            swap_data = [router.encodeABI(
                fn_name="exactInput",
                args=[(
                    path,
                    signer,
                    self.deadline(),
                    amount,
                    min_amount
                )]
            )]

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

                fee = await self.get_fee_by_url(gas_price=gas_price, gas_used=tx_rec['gasUsed'])
                tx_fee = f"tx fee ${fee}"

                logger.info(
                    f'||APPROVE| https://www.okx.com/explorer/zksync/tx/{approved_tx.hex()} '
                    f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
                )
                logger.info('Wait 30 sec.')

                await wait(_time=30)
            else:
                logger.info("Doesn't need approve. Wait 20 sec.")
                await wait(_time=5)
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

    async def get_eth_price(self, token0: ChecksumAddress, token1: ChecksumAddress) -> float:
        """Функция получения цены ETH"""

        quote = await self.get_price(token0=token0, token1=token1)
        return 1 / quote

    @staticmethod
    async def get_price(token0: ChecksumAddress, token1: ChecksumAddress) -> float:
        """Функция получения котировки на пару"""

        pairs = None
        attempts = 5

        async with aiohttp.ClientSession() as session:

            while not pairs and attempts != 0:
                try:
                    response = await session.get(
                        url=f"{cst.URL}{token0}%20{token1}"
                    )
                    data = await response.json()

                    pairs = data['pairs']
                except Exception as err:
                    logger.error(err)
                    attempts -= 1
                    time.sleep(2)

            for pair in pairs:

                if pair['dexId'] == 'syncswap':
                    price = float(pair['priceNative'])
                    break

        return price

    @staticmethod
    def generate_pool(token0: str, token1: str) -> str:
        """Функция получения пула для токенов"""

        if token0 == 'ETH':
            pool_name = f'{token0}/{token1}'
        else:
            pool_name = f'{token1}/{token0}'

        return cst.POOLS[pool_name]