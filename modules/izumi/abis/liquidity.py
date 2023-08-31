LIQ_ROUTER = [
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "miner",
                        "type": "address"
                    },
                    {
                        "internalType": "address",
                        "name": "tokenX",
                        "type": "address"
                    },
                    {
                        "internalType": "address",
                        "name": "tokenY",
                        "type": "address"
                    },
                    {
                        "internalType": "uint24",
                        "name": "fee",
                        "type": "uint24"
                    },
                    {
                        "internalType": "int24",
                        "name": "pl",
                        "type": "int24"
                    },
                    {
                        "internalType": "int24",
                        "name": "pr",
                        "type": "int24"
                    },
                    {
                        "internalType": "uint128",
                        "name": "xLim",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint128",
                        "name": "yLim",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint128",
                        "name": "amountXMin",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint128",
                        "name": "amountYMin",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deadline",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct LiquidityManager.MintParam",
                "name": "mintParam",
                "type": "tuple"
            }
        ],
        "name": "mint",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "lid",
                "type": "uint256"
            },
            {
                "internalType": "uint128",
                "name": "liquidity",
                "type": "uint128"
            },
            {
                "internalType": "uint256",
                "name": "amountX",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "amountY",
                "type": "uint256"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "bytes[]",
                "name": "data",
                "type": "bytes[]"
            }
        ],
        "name": "multicall",
        "outputs": [
            {
                "internalType": "bytes[]",
                "name": "results",
                "type": "bytes[]"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [],
        "name": "refundETH",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
]
