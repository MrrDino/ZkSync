import web3
import aiohttp

import settings as conf
import global_constants as gc

from loguru import logger
from web3 import AsyncWeb3
from web3.types import ChecksumAddress
from eth_account.signers.local import LocalAccount

from . import constants as cst
from .abis.pair import PAIR_ABI
from .abis.router import ROUTER_ABI
from .abis.manager import MANAGER_ABI
from general_abis.erc20 import ERC20_ABI
from helper import SimpleW3, retry, get_gas, wait, write_file


class PancakeSwap(SimpleW3):

    @retry
    async def start_swap(
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
        """Функция выполнения обмена для Pancakeswap"""

        token0, token1, signer, router = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )

        token_in = cst.TOKENS[token0.lower()]  # если ETH -> поведение меняется
        token_out = cst.TOKENS[token1.lower()]

        if token_in == 'ETH':
            pool = cst.POOLS[token_in + '/' + token_out]
        else:
            pool = cst.POOLS[token_out + '/' + token_in]

        rate = await self.get_rate(pool_address=pool)

        if isinstance(amount, float):
            amount = int(amount * rate * cst.SLIPPAGE * 10 ** cst.DECS[token_in])

        if token_in == 'ETH':
            decs = cst.DECS[token_out]
            amount_min = int((rate * (amount / 10 ** cst.DECS[token_in]) * cst.SLIPPAGE) * 10 ** decs)

            swap_data = [router.encodeABI(
                fn_name="exactInputSingle",
                args=[(token0, token1, cst.FEE, signer, amount, amount_min, cst.PRICE_LIMIT)]
            )]
        else:
            await self.approve(
                w3=w3,
                token=token0,
                signer=signer,
                amount=amount,
                account=account,
                spender=self.to_address(cst.ROUTER)
            )

            decs = cst.DECS[token_in]
            amount_min = int(((amount / 10 ** cst.DECS[token_out]) / rate * cst.SLIPPAGE) * 10 ** decs)

            data = [router.encodeABI(
                fn_name="exactInputSingle",
                args=[(token0, token1, cst.FEE, cst.ETH_RECIPIENT, amount, amount_min, cst.PRICE_LIMIT)]
            )]
            swap_data = data + [router.encodeABI(fn_name='unwrapWETH9', args=[amount_min, signer])]

        swap_tx = await router.functions.multicall(
            self.deadline(),
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
        swap_tx['maxFeePerGas'] = int(gas_price * 1.1)
        swap_tx['maxPriorityFeePerGas'] = gas_price
        swap_tx['gas'] = await w3.eth.estimate_gas(swap_tx)

        signed_tx = account.sign_transaction(transaction_dict=swap_tx)
        logger.info("Swap transaction signed.")
        await wait(_time=20)

        status = 0

        try:
            swap_tx = await w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
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

    @retry
    async def add_liquidity(self, token0: str, key: str, mode: int = 1):
        """Функция добавления ликвидности для Mute.io"""

        amount = None
        w3 = await self.connect()
        token1 = self.to_address(gc.ETH)
        account = self.get_account(w3=w3, key=key)

        token0, token1, signer, _ = self.prepare(
            w3=w3,
            token0=token0,
            token1=token1,
            account=account
        )
        router = self.get_contract(w3=w3, address=cst.POSITION_MANAGER, abi=MANAGER_ABI)

        token_in = cst.TOKENS[token0.lower()]  # если ETH -> поведение меняется
        token_out = cst.TOKENS[token1.lower()]

        eth = await self.get_rate(
            pool_address=AsyncWeb3.to_checksum_address("0x291d9f9764c72c9ba6ff47b451a9f7885ebf9977")
        )
        eth = 1 / eth

        if not amount:
            need_msg = True

            while not amount:
                amount = await self.get_amount(w3=w3, wallet=account.address, mode=mode, eth=eth)

                if not amount:
                    if need_msg:
                        logger.error(f"Insufficient balance! Address - {account.address} key - {key}")
                        need_msg = False
                    await wait(_time=conf.TOP_UP_WAIT)

        if token_in == 'ETH':
            pool_address = cst.POOLS[token_in + '/' + token_out]
        else:
            pool_address = cst.POOLS[token_out + '/' + token_in]

        rate = await self.get_rate(pool_address=pool_address)

        balance_check = await self.check_balance(
            w3=w3,
            rate=rate,
            token=token0,
            wallet=signer,
            amount=amount,
            token_in=token_in,
        )

        if not balance_check:
            logger.info(f"Insufficient balance of token \33[{36}m{token0}\033[0m")
            return False

        await self.approve(
            w3=w3,
            token=token0,
            signer=signer,
            amount=amount,
            account=account,
            spender=self.to_address(cst.POSITION_MANAGER)
        )

        pool = self.get_contract(w3=w3, address=pool_address, abi=PAIR_ABI)
        data = await pool.functions.slot0().call()

        tick = data[1]

        if tick > 0:
            tick_lower = self.round_int(num=int(tick * cst.TICKS[0]))
            tick_upper = self.round_int(num=int(tick * cst.TICKS[1]))
        else:
            tick_lower = self.round_int(num=int(tick * cst.TICKS[1]))
            tick_upper = self.round_int(num=int(tick * cst.TICKS[0]))

        decs = cst.DECS[token_in]
        amount0 = int(((amount / 10 ** cst.DECS[token_out]) * rate) * 10 ** decs)

        liq_data = router.encodeABI(
                fn_name="mint",
                args=[(
                    token0,
                    token1,
                    cst.FEE,
                    tick_lower,
                    tick_upper,
                    amount0,
                    amount,
                    0,
                    0,
                    signer,
                    self.deadline()
                )]
            )

        liq_tx = await router.functions.multicall(
            [liq_data]
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

        signed_tx = account.sign_transaction(transaction_dict=liq_tx)
        logger.info("Liquidity transaction signed.")
        await wait(_time=20)

        status = 0

        try:
            swap_tx = await w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = await w3.eth.wait_for_transaction_receipt(swap_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = await self.get_fee_by_url(gas_price=gas_price, gas_used=tx_rec['gasUsed'])
            tx_fee = f"tx fee ${fee}"
            link = f"https://www.okx.com/explorer/zksync/tx/{swap_tx.hex()}"
            write_file(wallet=signer, tx=link, action=2, status=status)

            logger.info(
                f'||ADD LIQ {token_in}/{token_out}| {link} '
                f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
            )
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

        assert status == 1  # если статус != 1 транзакция не прошла

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

                await wait(_time=30)
            else:
                logger.info("Doesn't need approve.")
                await wait(_time=5)
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

    async def check_balance(
            self,
            w3: AsyncWeb3,
            rate: float,
            amount: int,
            token_in: str,
            token: ChecksumAddress,
            wallet: ChecksumAddress
    ) -> bool:
        """Функция проверки баланса для добавления ликвидности"""

        token_contract = self.get_contract(w3=w3, address=token, abi=ERC20_ABI)
        balance = await token_contract.functions.balanceOf(wallet).call() / 10 ** cst.DECS[token_in]

        token_balance = balance * rate

        if token_balance > (amount / 10 ** 18):
            return True
        else:
            return False

    @staticmethod
    def round_int(num: int):

        remain = num % 10
        return num + 10 - remain

    @staticmethod
    async def get_rate(pool_address: ChecksumAddress) -> float:
        """Функция получения информации о цене с Coingecko"""

        price = None
        attempts = 5

        pool_address = pool_address.lower()

        async with aiohttp.ClientSession() as session:

            while not price and attempts != 0:
                try:
                    response = await session.get(
                        url="https://api.geckoterminal.com/api/v2/networks/zksync/dexes/pancakeswap-v3-zksync/pools"
                    )
                    data = await response.json()

                    for item in data['data']:
                        item = item['attributes']

                        if item['address'] == pool_address:
                            price = round(float(item['quote_token_price_usd']) / float(item['base_token_price_usd']), 2)
                            return price

                except Exception as err:
                    logger.error(err)
                    attempts -= 1
                    await wait(_time=2)
