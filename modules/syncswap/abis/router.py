ROUTER_ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_vault",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "_wETH",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [],
        "name": "ApproveFailed",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "Expired",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "NotEnoughLiquidityMinted",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "TooLittleReceived",
        "type": "error"
    },
    {
        "inputs": [],
        "name": "TransferFromFailed",
        "type": "error"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "pool",
                "type": "address"
            },
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "token",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "amount",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct SyncSwapRouter.TokenInput[]",
                "name": "inputs",
                "type": "tuple[]"
            },
            {
                "internalType": "bytes",
                "name": "data",
                "type": "bytes"
            },
            {
                "internalType": "uint256",
                "name": "minLiquidity",
                "type": "uint256"
            },
            {
                "internalType": "address",
                "name": "callback",
                "type": "address"
            },
            {
                "internalType": "bytes",
                "name": "callbackData",
                "type": "bytes"
            }
        ],
        "name": "addLiquidity2",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "liquidity",
                "type": "uint256"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "",
                "type": "address"
            }
        ],
        "name": "isPoolEntered",
        "outputs": [
            {
                "internalType": "bool",
                "name": "",
                "type": "bool"
            }
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
                    {
                        "components": [
                            {
                                "internalType": "address",
                                "name": "pool",
                                "type": "address"
                            },
                            {
                                "internalType": "bytes",
                                "name": "data",
                                "type": "bytes"
                            },
                            {
                                "internalType": "address",
                                "name": "callback",
                                "type": "address"
                            },
                            {
                                "internalType": "bytes",
                                "name": "callbackData",
                                "type": "bytes"
                            }
                        ],
                        "internalType": "struct IRouter.SwapStep[]",
                        "name": "steps",
                        "type": "tuple[]"
                    },
                    {
                        "internalType": "address",
                        "name": "tokenIn",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "amountIn",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct IRouter.SwapPath[]",
                "name": "paths",
                "type": "tuple[]"
            },
            {
                "internalType": "uint256",
                "name": "amountOutMin",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "deadline",
                "type": "uint256"
            }
        ],
        "name": "swap",
        "outputs": [
            {
                "components": [
                    {
                        "internalType": "address",
                        "name": "token",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "amount",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct IPool.TokenAmount",
                "name": "amountOut",
                "type": "tuple"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    }
]
