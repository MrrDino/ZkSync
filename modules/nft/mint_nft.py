import time
import random

from web3 import Web3
from loguru import logger
from eth_abi import encode
from web3.types import ChecksumAddress
from web3.exceptions import ContractLogicError
from eth_account.signers.local import LocalAccount
from web3.middleware import construct_sign_and_send_raw_middleware

from . import constants as cst
from helper import SimpleW3, retry, get_gas


class Minter(SimpleW3):

    def start_mint(self, key: str):
        """Функция запуска минта NFT"""

        w3 = self.connect()
        account = self.get_account(w3=w3, key=key)
        w3.middleware_onion.add(construct_sign_and_send_raw_middleware(account))

        signer = account.address

        numbers = [i for i in range(0, 5)]
        minted = 0

        for i in range(0, len(numbers)):

            if minted == 2:
                break

            number = random.choice(numbers)
            numbers.remove(number)

            result = self.mint(w3=w3, account=account, signer=signer, number=number)

            if result:
                minted += 1

        logger.info(
            f"Account \33[{35}m{account.address}\033[0m mint \33[{36}m{minted}\033[0m NFTs"
        )

    @retry
    def mint(self, w3: Web3, account: LocalAccount, signer: ChecksumAddress, number: int) -> bool:
        """Функция минта NFT"""

        if not (0 <= number <= 5):
            logger.error(f'\33[{31}mInvalid number: {number}\033[0m')
            raise Exception

        status = 0
        mint_data = cst.MINT

        data = '0x57bc3d78' + encode(['address', 'uint8'], [signer, number]).hex() + mint_data
        gas_price = w3.eth.gas_price

        tx = {
            'from': signer,
            'to': Web3.to_checksum_address('0x3F9931144300f5Feada137d7cfE74FAaa7eF6497'),
            'nonce': w3.eth.get_transaction_count(signer),
            'value': 0,
            'data': data,
            'chainId': w3.eth.chain_id,
            'maxFeePerGas': int(gas_price * 1.1),
            'maxPriorityFeePerGas': gas_price
        }

        try:
            tx['gas'] = int(w3.eth.estimate_gas(tx) * 1.1)
        except ContractLogicError:
            logger.error(f"NFT with number \33[{35}m{number}\033[0m already minted!")
            return False

        try:
            signed_tx = account.sign_transaction(tx)
            logger.info("Mint transaction signed. Wait 30 sec.")
            time.sleep(30)

            mint_tx = w3.eth.send_raw_transaction(signed_tx.rawTransaction)
            tx_rec = w3.eth.wait_for_transaction_receipt(mint_tx)

            gas = get_gas()
            status = tx_rec['status']
            fee = self.get_fee_by_url(gas_price=gas_price, gas_used=tx_rec['gasUsed'])
            tx_fee = f"tx fee ${fee}"

            logger.info(
                f'||MINT NFT| https://www.okx.com/explorer/zksync/tx/{mint_tx.hex()} '
                f'Gas: {gas} gwei, \33[{36}m{tx_fee}\033[0m'
            )
        except Exception as err:
            logger.error(f"\33[{31}m{err}\033[0m")

        assert status == 1  # если статус != 1 транзакция не прошла

        return True
