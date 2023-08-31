ROUTER_ABI = [
    {
        "inputs": [
            {
                "components": [
                    {
                        "internalType": "bytes",
                        "name": "path",
                        "type": "bytes"
                    },
                    {
                        "internalType": "address",
                        "name": "recipient",
                        "type": "address"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deadline",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "amountIn",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "amountOutMinimum",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct IRouter.ExactInputParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "exactInput",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "amountOut",
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
        "type": "function"},
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "amountMinimum",
                "type": "uint256"
            },
            {
                "internalType": "address",
                "name": "recipient",
                "type": "address"
            }
        ],
        "name": "unwrapWETH9",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "internalType": "contract IPool",
                "name": "pool",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "tokenId",
                "type": "uint256"
            },
            {
                "components": [
                    {
                        "internalType": "uint8",
                        "name": "kind",
                        "type": "uint8"
                    },
                    {
                        "internalType": "int32",
                        "name": "pos",
                        "type": "int32"
                    },
                    {
                        "internalType": "bool",
                        "name": "isDelta",
                        "type": "bool"
                    },
                    {
                        "internalType": "uint128",
                        "name": "deltaA",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint128",
                        "name": "deltaB",
                        "type": "uint128"
                    }
                ],
                "internalType": "struct IPool.AddLiquidityParams[]",
                "name": "params",
                "type": "tuple[]"
            },
            {
                "internalType": "uint256",
                "name": "minTokenAAmount",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "minTokenBAmount",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "deadline",
                "type": "uint256"
            }
        ],
        "name": "addLiquidityToPool",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "receivingTokenId",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "tokenAAmount",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "tokenBAmount",
                "type": "uint256"
            },
            {
                "components": [
                    {
                        "internalType": "uint128",
                        "name": "deltaA",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint128",
                        "name": "deltaB",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deltaLpBalance",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint128",
                        "name": "binId",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint8",
                        "name": "kind",
                        "type": "uint8"
                    },
                    {
                        "internalType": "int32",
                        "name": "lowerTick",
                        "type": "int32"
                    },
                    {
                        "internalType": "bool",
                        "name": "isActive",
                        "type": "bool"
                    }
                ],
                "internalType": "struct IPool.BinDelta[]",
                "name": "binDeltas",
                "type": "tuple[]"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
]
