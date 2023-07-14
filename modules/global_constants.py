ETH_NODE = 'https://rpc.ankr.com/eth'

MAX_GAS = 20

TIMEOUT = 10

# SWAP SIZE
SWAP_AMOUNT = (.0040783968, .007646994)
MIN_AMOUNT = .0040783968  # ETH
MAX_AMOUNT = .007646994  # ETH

# LIQUIDITY SIZE
LIQ_AMOUNT = (.0040783968, .007646994)


SWAP_BACK = True  # Нужно ли менять актив обратно


EXCHANGES = {
    0: 'Mute',
    1: 'Velocore',
    2: 'SyncSwap',
    3: 'SpaceFi'
}

DELAY1 = (10, 60)  # timeout between swaps
DELAY2 = (10, 60)  # timeout between swap & liquidity
DELAY3 = (10, 60)  # timeout between liquidity & shit coin
DELAY4 = (10, 60)  # timeout between wallets


ETH = '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'


SWAP = {
    'Mute': [
        '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4',  # USDC
        '0x503234f203fc7eb888eec8513210612a43cf6115',  # LUSD
        '0x8e86e46278518efc1c5ced245cba2c7e3ef11557'  # USD+
    ],
    'Velocore': [
        '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4',  # USDC
        '0x2039bb4116b4efc145ec4f0e2ea75012d6c0f181',  # BUSD
        '0x8e86e46278518efc1c5ced245cba2c7e3ef11557'  # USD+
    ],
    'SyncSwap': [
        '0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181',  # BUSD
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',  # USDC
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',  # USDT
        '0xfC7E56298657B002b3e656400E746b7212912757',  # ZkUSD
        '0x503234F203fC7Eb888EEC8513210612a43Cf6115',  # LUSD
        '0x8e86e46278518efc1c5ced245cba2c7e3ef11557',  # USD+
        '0xb4c1544cb4163f4c2eca1ae9ce999f63892d912a',  # FRAX
    ],
    'SpaceFi': [
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',  # USDC
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',  # USDT
        '0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181',  # BUSD
        '0xfC7E56298657B002b3e656400E746b7212912757',  # ZkUSD
        '0x503234F203fC7Eb888EEC8513210612a43Cf6115',  # LUSD
        '0x8e86e46278518efc1c5ced245cba2c7e3ef11557',  # USD+
        '0xb4c1544cb4163f4c2eca1ae9ce999f63892d912a',  # FRAX
    ]
}

LIQ = {
    'Mute': [
        '0x503234f203fc7eb888eec8513210612a43cf6115',  # LUSD
        '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4'  # USDC
    ],
    'Velocore': [
        '0x2039bb4116b4efc145ec4f0e2ea75012d6c0f181',  # BUSD
        '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4',  # USDC
    ],
    'SyncSwap': [

    ],
    'SpaceFi': [

    ]
}

SHIT_COINS = [
    '0x6068ad384b4d330d4de77f47041885956c9f32a3',  # Array -> SpaceFi
    '0xbbd1ba24d589c319c86519646817f2f153c9b716',  # Rhino.fi -> SyncSwap, SpaceFi
    '0x0e97c7a0f8b2c9885c8ac9fc6136e829cbc21d42',  # MUTE -> SyncSwap, SpaceFi
    '0xd0ea21ba66b67be636de1ec4bd9696eb8c61e9aa'  # Onchain Trade -> SyncSwap, SpaceFi
    '0xfd282f16a64c6d304ac05d1a58da15bed0467c71'  # PEPE -> SyncSwap, SpaceFi
    '0x47260090cE5e83454d5f05A0AbbB2C953835f777'  # SPACE -> SyncSwap, SpaceFi
    '0x85d84c774cf8e9ff85342684b0e795df72a24908'  # Velocore -> SyncSwap, SpaceFi
    '0xbbeb516fb02a01611cbbe0453fe3c580d7281011'  # Wrapped BTC -> SyncSwap, SpaceFi
    '0x47ef4a5641992a72cfd57b9406c9d9cefee8e0c4'  # zkApes Token -> SyncSwap, SpaceFi
    '0xb54aae4a0743aeec1d584f2b2abc1ebdc12f1b0f'  # frx ETH -> SyncSwap, SpaceFi
]