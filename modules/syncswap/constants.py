from web3 import Web3

WITHDRAW_MODE = 1

# RPC_NODE = 'https://rpc.ankr.com/zksync_era'

USDT = '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C'
USDC = '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4'
ETH = '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'

ROUTER = '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295'
POOL_FACTORY = '0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb'


ZERO_ADDRESS = Web3.to_checksum_address('0x000000000000000000000000000000000000800A')


TOKENS = {
    '0x493257fd37edb34451f62edf8d2a0c418852ba4c': 'USDT',
    '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4': 'USDC',
    '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91': 'ETH',
}


#  В пулах со стейбл коинами не точное соотношения, для этого нужны данные погрешности
MULTS = {
    '0x493257fd37edb34451f62edf8d2a0c418852ba4c': .006,
    '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4': .0034
}