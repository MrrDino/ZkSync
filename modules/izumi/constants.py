ROUTER = '0x943ac2310D9BC703d6AB5e5e76876e212100f894'


HEADERS = {
    'authority': 'api.izumi.finance',
    'accept': 'application/json, text/plain, */*',
    'accept-language': 'ru,en;q=0.9',
    'origin': 'https://zksync.izumi.finance',
    'referer': 'https://zksync.izumi.finance/',
    'sec-ch-ua': '"Chromium";v="112", "YaBrowser";v="23", "Not:A-Brand";v="99"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
                  ' Chrome/112.0.0.0 YaBrowser/23.5.4.674 Yowser/2.5 Safari/537.36',

}


USDC = '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4'
ETH = '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91'
USDT = '0x496d88D1EFc3E145b7c12d53B78Ce5E7eda7a42c'


TOKENS = {
    '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf4': 'USDC',
    '0x5aea5775959fbc2557cc8789bc1bf90a239d9a91': 'ETH',
    '0x496d88d1efc3e145b7c12d53b78ce5e7eda7a42c': 'USDT',
}


PATHS = {
    'USDC': {
        'in': '0x5aea5775959fbc2557cc8789bc1bf90a239d9a910x07d03355df6d4c9c3035724fd0e3914de96a5a83aaf4',
        'out': '0x3355df6d4c9c3035724fd0e3914de96a5a83aaf40001905aea5775959fbc2557cc8789bc1bf90a239d9a91'
    },
    'USDT': {
        'in': '0x5aea5775959fbc2557cc8789bc1bf90a239d9a910001903355df6d4c9c3035724fd0e3914de96a5a83aaf40001900x496d88d1efc3e145b7c12d53b78ce5e7eda7a42c',
        'out': '0x496d88d1efc3e145b7c12d53b78ce5e7eda7a42c0001903355df6d4c9c3035724fd0e3914de96a5a83aaf40001905aea5775959fbc2557cc8789bc1bf90a239d9a91'
    }
}


DECIMALS = {
    'USDT': 6,
    'USDC': 6,
    'ETH': 18
}