from web3 import Web3


WITHDRAW_MODE = 1


MINT = 0
MIN_LIQ = 0


ROUTER = '0x2da10A1e27bF85cEdD8FFb1AbBe97e53391C0295'
FACTORY = '0xf2DAd89f2788a8CD54625C60b55cD3d2D0ACa7Cb'


ZERO_ADDRESS = Web3.to_checksum_address('0x0000000000000000000000000000000000000000')


TOKENS = {
    '0x493257fd37edb34451f62edf8d2a0c418852ba4c': 'USDT',
    '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4': 'USDC',
    '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91': 'ETH',
    '0x2039bb4116b4efc145ec4f0e2ea75012d6c0f181': 'BUSD',
    '0xfc7e56298657b002b3e656400e746b7212912757': 'ZkUSD',
    '0x503234f203fc7eb888eec8513210612a43cf6115': 'LUSD',
    '0x8e86e46278518efc1c5ced245cba2c7e3ef11557': 'USD+',
    '0xb4c1544cb4163f4c2eca1ae9ce999f63892d912a': 'FRAX',
    '0xbbd1ba24d589c319c86519646817f2f153c9b716': 'DVF',
    '0x0e97c7a0f8b2c9885c8ac9fc6136e829cbc21d42': 'MUTE',
    '0xd0ea21ba66b67be636de1ec4bd9696eb8c61e9aa': 'OT',
    '0xfd282f16a64c6d304ac05d1a58da15bed0467c71': 'PEPE',
    '0x47260090ce5e83454d5f05a0abbb2c953835f777': 'SPACE',
    '0x85d84c774cf8e9ff85342684b0e795df72a24908': 'VC',
    '0xbbeb516fb02a01611cbbe0453fe3c580d7281011': 'WBTC',
    '0x47ef4a5641992a72cfd57b9406c9d9cefee8e0c4': 'ZAT',
    '0xb54aae4a0743aeec1d584f2b2abc1ebdc12f1b0f': 'frxETH'
}


#  В пулах со стейбл коинами не точное соотношение, для этого нужны данные погрешности
MULTS = {
    '0x493257fd37edb34451f62edf8d2a0c418852ba4c': .006,  # USDT
    '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4': .0034,  # USDC
    '0x2039bb4116b4efc145ec4f0e2ea75012d6c0f181': .002,  # BUSD
    '0xfc7e56298657b002b3e656400e746b7212912757': .002,  # ZkUSD
    '0x503234f203fc7eb888eec8513210612a43cf6115': .002,  # LUSD
    '0x8e86e46278518efc1c5ced245cba2c7e3ef11557': .0007,  # USD+
    '0xb4c1544cb4163f4c2eca1ae9ce999f63892d912a': .004,  # FRAX
}

# '0xb4c1544cb4163f4c2eca1ae9ce999f63892d912a',  # FRAX <- не поменялся обратно
