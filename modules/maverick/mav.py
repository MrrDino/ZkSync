import time
import requests

import global_constants as gc

from web3 import Web3
from loguru import logger
from web3.types import ChecksumAddress
from requests.adapters import HTTPAdapter, Retry
from eth_account.signers.local import LocalAccount

from . import constants as cst
from .abis.router import ROUTER_ABI
from helper import SimpleW3, retry, get_gas


class Maverick(SimpleW3):


    # @retry
    def make_swap(
            self,
            key: str,
            token0: str,
            token1: str,
            mode: int = 0,
            amount: float = None
    ):
        """Функция выполнения обмена для Maverick"""

        status = 0
        w3 = self.connect()
        account = self.get_account(w3=w3, key=key)

        signer = account.address
        token0 = self.to_address(token0)
        token1 = self.to_address(token1)
        token_in = cst.TOKENS[token0.lower()]
        token_out = cst.TOKENS[token1.lower()]
        router = self.get_contract(w3=w3, address=cst.ROUTER, abi=ROUTER_ABI)
        pool_address = self.generate_pool(token0=token_in, token1=token_out)
        path = f'0x{token0[2:]}{pool_address[2:]}{token1[2:]}'

        if not amount:
            need_msg = True

            while not amount:
                amount = self.get_amount(w3=w3, wallet=account.address, mode=mode)

                if not amount:
                    if need_msg:
                        logger.error(f"Insufficient balance! Address - {account.address} key - {key}")
                        need_msg = False
                    time.sleep(gc.TOP_UP_WAIT)

            value = amount
            data_for_unwrap = [router.encodeABI(fn_name='refundETH', args=[])]

            quote = self.get_price(token0=token0, token1=token1)
            min_amount = (quote * (amount / 10 ** 18)) * 10 ** cst.DECIMALS[token0.lower()]
            min_amount = int(min_amount - min_amount * cst.SLIPPAGE)
        else:
            value = 0
            data_for_unwrap = [router.encodeABI(fn_name='unwrapWETH9', args=[0, signer])]

            quote = self.get_price(token0=token0, token1=token1)
            min_amount = int((amount - amount * cst.SLIPPAGE) * 10 ** 18)  # HARDCODE DECS ETH
            amount = int((amount * quote) * 10 ** cst.DECIMALS[token0.lower()])

        if token_in != 'ETH':
            self.approve(
                w3=w3,
                token=token0,
                signer=signer,
                amount=amount,
                account=account,
                spender=cst.ROUTER
            )

        args = path, '0x0000000000000000000000000000000000000000', self.deadline(), amount, min_amount

        input_data = router.encodeABI(
            fn_name='exactInput',
            args=[args]
        )

        data = [input_data] + data_for_unwrap
        tx = self.build_tx(w3, signer, router,  'multicall', value, args=data)

        try:
            signed_tx = account.sign_transaction(tx)

            swap_tx = w3.eth.send_raw_transaction(transaction=signed_tx.rawTransaction)
            tx_rec = w3.eth.wait_for_transaction_receipt(swap_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = self.get_fee_by_url(gas_price=w3.eth.gas_price, gas_used=tx_rec['gasUsed'])

            tx_fee = f"tx fee ${fee}"

            logger.info(
                f'||SWAP to {token_out}| https://www.okx.com/explorer/zksync/tx/{swap_tx.hex()} '
                f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
            )
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

        assert status == 1  # если статус != 1 транзакция не прошла

    def approve(
            self,
            w3: Web3,
            amount: int,
            account: LocalAccount,
            token: ChecksumAddress,
            signer: ChecksumAddress,
            spender: ChecksumAddress,
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

                fee = self.get_fee_by_url(gas_price=gas_price, gas_used=tx_rec['gasUsed'])

                tx_fee = f"tx fee ${fee}"

                logger.info(
                    f'||APPROVE| https://www.okx.com/explorer/zksync/tx/{approved_tx.hex()} '
                    f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
                )
                logger.info('Wait 30 sec.')

                time.sleep(30)
            else:
                logger.info("Doesn't need approve. Wait 20 sec.")
                time.sleep(20)
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

    def get_eth_price(self, token0: ChecksumAddress, token1: ChecksumAddress) -> float:
        """Функция получения цены ETH"""

        quote = self.get_price(token0=token0, token1=token1)
        return 1 / quote

    @staticmethod
    def get_price(token0: ChecksumAddress, token1: ChecksumAddress) -> float:
        """Функция получения котировки на пару"""

        pairs = None
        attempts = 5
        client = requests.Session()
        retries = Retry(
            total=15,
            backoff_factor=0.1,
            status_forcelist=[500, 502, 503, 504]
        )

        client.mount('http://', HTTPAdapter(max_retries=retries))

        while not pairs and attempts != 0:
            try:
                response = client.get(
                    url=f"{cst.URL}{token0}%20{token1}"
                )

                if response.status_code != 200:
                    raise Exception

                pairs = response.json()['pairs']
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

    @staticmethod
    def build_tx(w3, address, router, func=None, value=0, args=None) -> dict:

        nonce = w3.eth.get_transaction_count(address)
        func_ = getattr(router.functions, func)

        if type(args) != list:
            tx = func_(*args).build_transaction({
                'from': address,
                'nonce': nonce,
                'value': value,
                'maxFeePerGas': int(w3.eth.gas_price * 1.1),
                'maxPriorityFeePerGas': w3.eth.gas_price
            })
            tx['gas'] = int(w3.eth.estimate_gas(tx))
        else:
            tx = func_(args).build_transaction({
                'from': address,
                'nonce': nonce,
                'value': value,
                'maxFeePerGas': int(w3.eth.gas_price * 1.1),
                'maxPriorityFeePerGas': w3.eth.gas_price
            })
            tx['gas'] = int(w3.eth.estimate_gas(tx))

        return tx


# {'gas': 442751, 'chainId': 324, 'from': '0x70582751e8BE8d169C180f78D1c434ba0d9d6bC9', 'nonce': 199, 'value': 5915081740083082, 'maxFeePerGas': 275000000, 'maxPriorityFeePerGas': 250000000, 'to': '0xbBF1EE38152E9D8e3470Dc47947eAa65DcA94913', 'data': '0xac9650d800000000000000000000000000000000000000000000000000000000000000200000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000004000000000000000000000000000000000000000000000000000000000000001a00000000000000000000000000000000000000000000000000000000000000124c04b8d59000000000000000000000000000000000000000000000000000000000000002000000000000000000000000000000000000000000000000000000000000000a000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000064b8b956000000000000000000000000000000000000000000000000001503bc49ef5f8a00000000000000000000000000000000000000000000000099c2e3848f331000000000000000000000000000000000000000000000000000000000000000003c5aea5775959fbc2557cc8789bc1bf90a239d9a9174a8f079eb015375b5dbb3ee98cbb1b91089323f3355df6d4c9c3035724fd0e3914de96a5a83aaf40000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000004449404b7c000000000000000000000000000000000000000000000000000000000000000000000000000000000000000070582751e8be8d169c180f78d1c434ba0d9d6bc900000000000000000000000000000000000000000000000000000000'}
