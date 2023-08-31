# Основные константы
ETH_NODE = 'https://rpc.ankr.com/eth'  # адрес ноды в сети Ethereum
ZK_NODE = 'https://rpc.ankr.com/zksync_era'  # адрес ноды в сети ZkSync

USDC = '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4'  # адрес USDC в сети ZkSync
ETH = '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'  # адрес ETH в сети ZkSync
USDT = "0x493257fD37EDB34451f62EDf8D2a0C418852bA4C"

USDC_DECS = 6  # кол-во десятков при переводе в USDC
ETH_DECS = 18  # кол-во десятков при переводе в ETH


# Спсиок действий, которые присутствуют в скрипте
ACTIONS_ = {
    0: "swap",
    1: "swap_back",
    2: "liq",
    3: "nft",
    4: "shit"
}


# Обмен токенов

# Список бирж, с которыми работает код
EXCHANGES = [
    'Mute',
    'Izumi',
    'SpaceFi',
    'Pancake',
    'Maverick',
    'Velocore',
    'SyncSwap',
]


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
    ],
    'SpaceFi': [
        '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4',  # USDC
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',  # USDT
        '0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181',  # BUSD,
        '0xfC7E56298657B002b3e656400E746b7212912757',  # ZkUSD,
        '0x503234F203fC7Eb888EEC8513210612a43Cf6115',  # LUSD,
        '0x8e86e46278518efc1c5ced245cba2c7e3ef11557',  # USD+,
        # '0xb4c1544cb4163f4c2eca1ae9ce999f63892d912a',  # FRAX,
    ],
    'Pancake': [
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',  # USDC
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',  # USDT
        '0x2039bb4116B4EFc145Ec4f0e2eA75012D6C0f181',  # BUSD,
    ],
    'Maverick': [
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',  # USDC
    ],
    'Izumi': [
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',  # USDC
        # '0x496d88d1efc3e145b7c12d53b78ce5e7eda7a42c',  # USDT
    ]
}


# Добавление ликвидности
LIQ = {
    'Mute': [
        # '0x0e97c7a0f8b2c9885c8ac9fc6136e829cbc21d42',  # MUTE
        '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4',  # USDC
        # '0xbbeb516fb02a01611cbbe0453fe3c580d7281011',  # WBTC
    ],
    'Velocore': [
        '0x8e86e46278518efc1c5ced245cba2c7e3ef11557',  # USD+,
        # '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4',  # USDC
    ],
    'SyncSwap': [
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',  # USDC
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',  # USDT
        # '0xbbeb516fb02a01611cbbe0453fe3c580d7281011',  # WBTC
    ],
    'SpaceFi': [
        # '0x0e97c7a0f8b2c9885c8ac9fc6136e829cbc21d42',  # MUTE
        '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4',  # USDC
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',  # USDT
    ],
    'Pancake': [
        '0x3355df6D4c9C3035724Fd0e3914dE96A5a83aaf4',  # USDC
        '0x493257fD37EDB34451f62EDf8D2a0C418852bA4C',  # USDT
    ]
}


# Покупка шиткоинов
SHIT_COINS = [
    '0xbbd1ba24d589c319c86519646817f2f153c9b716',  # Rhino.fi
    '0x0e97c7a0f8b2c9885c8ac9fc6136e829cbc21d42',  # MUTE
    '0xd0ea21ba66b67be636de1ec4bd9696eb8c61e9aa',  # Onchain Trade
    '0xfd282f16a64c6d304ac05d1a58da15bed0467c71',  # PEPE
    '0x47260090cE5e83454d5f05A0AbbB2C953835f777',  # SPACE
    '0x85d84c774cf8e9ff85342684b0e795df72a24908',  # Velocore
    '0xbbeb516fb02a01611cbbe0453fe3c580d7281011',  # Wrapped BTC
    '0x47ef4a5641992a72cfd57b9406c9d9cefee8e0c4',  # zkApes Token
    '0xb54aae4a0743aeec1d584f2b2abc1ebdc12f1b0f',  # frx ETH
]

# ключи для записи в файл результатов
ACTIONS = {
    0: "Swap",
    1: "Add liquidity",
    2: "Mint NFT",
    3: "Buy shitcoin"
}

# Названия столбцов файла с результатами
CSV_COLUMNS = ['Wallet', 'Time', "Tx", "Action", "Status"]


# Ожидания при работе с транзакциями
BUILD_DELAY = [17, 28]
SIGN_DELAY = [23, 39]
SEND_DELAY = [21, 43]
