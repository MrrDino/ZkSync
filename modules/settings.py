# DIVIDER = 10  # количество кошельков, используемых в одном потоке
STREAMS = 1  # количество потоков, идущих одновременно
MAX_GAS = 100  # максимальный газ в сети Ethereum (Gwei)

# Ожидания
TIMEOUT = 10  # ожидание, когда газ выше MAX_GAS или количество прокси не соответствует количеству кошельков
TOP_UP_WAIT = 10  # ожидание пока кошелек пополнитмя
DELAY1 = (10, 60)  # ожидание между свапами (если SWAP_BACK=True)
DELAY2 = (10, 60)  # ожидание между свапом на бирже и пополнением ликвидности
DELAY3 = (10, 60)  # ожидание между поплнением ликвидности и покупкой шиткоина
DELAY4 = (10, 60)  # ожидание между покупкой шиткоина и минтом NFT
DELAY5 = (10, 60)  # ожидание между сменой кошельков


# Обмен токенов
# ВКЛ/ВЫКЛ = TRUE/False
EXCHANGES_STATUS = {
    'Mute': True,  # включена ли биржа Mute
    'SpaceFi': False,  # включена ли биржа SpaceFi
    'Velocore': True,  # включена ли биржа Velocore
    'SyncSwap': True,  # включена ли биржа SyncSwap
    'Pancake': True  # включена ли биржа Pancake
}

SWAP_BACK = True  # нужно ли производить обратный свап


# Добавление ликвидности
NEED_LIQ = True  # включен ли модуль добавления ликвидности
MAX_PRICE_IMPACT = 0.005  # максимальное влияние на цену при поплнении ликвидности (price impact)
MIN_LIQUIDITY = 1_000_000  # минамальная ликвидность пула для пула, в котором пополняется ликвидность


# NFT
MAX_NFTS = 2  # кол-во NFT к минту (не больше 4)
NEED_NFT = True  # включен ли модуль NFT


# Покупка шиткоинов
NEED_SHITCOIN = True  # включен ли модуль покупки шиткоинов

AMOUNTS = {
    0: (0.0040783968, 0.006646994),  # сумма обмена токенов в ETH
    1: (50, 250),  # сумма добавления ликвидности в центах
    2: (0.0040783968, 0.006046994)  # сумма покупки шиткоинов в ETH
}

