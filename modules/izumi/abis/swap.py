SWAP_ABI = [
    {
        "inputs": [
            {
                "internalType": "address",
                "name": "_factory",
                "type": "address"
            },
            {
                "internalType": "address",
                "name": "_weth",
                "type": "address"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "constructor"
    },
    {
        "inputs": [
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
            }
        ],
        "name": "pool",
        "outputs": [
            {
                "internalType": "address",
                "name": "",
                "type": "address"
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
                        "internalType": "uint128",
                        "name": "amount",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint256",
                        "name": "minAcquired",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deadline",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct Swap.SwapAmountParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "swapAmount",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "cost",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "acquire",
                "type": "uint256"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
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
                        "internalType": "uint128",
                        "name": "desire",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint256",
                        "name": "maxPayed",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deadline",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct Swap.SwapDesireParams",
                "name": "params",
                "type": "tuple"
            }
        ],
        "name": "swapDesire",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "cost",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "acquire",
                "type": "uint256"
            }
        ],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
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
                        "name": "boundaryPt",
                        "type": "int24"
                    },
                    {
                        "internalType": "address",
                        "name": "recipient",
                        "type": "address"
                    },
                    {
                        "internalType": "uint128",
                        "name": "amount",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint256",
                        "name": "maxPayed",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "minAcquired",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deadline",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct Swap.SwapParams",
                "name": "swapParams",
                "type": "tuple"
            }
        ],
        "name": "swapX2Y",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
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
                        "name": "boundaryPt",
                        "type": "int24"
                    },
                    {
                        "internalType": "address",
                        "name": "recipient",
                        "type": "address"
                    },
                    {
                        "internalType": "uint128",
                        "name": "amount",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint256",
                        "name": "maxPayed",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "minAcquired",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deadline",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct Swap.SwapParams",
                "name": "swapParams",
                "type": "tuple"
            }
        ],
        "name": "swapX2YDesireY",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
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
                        "name": "boundaryPt",
                        "type": "int24"
                    },
                    {
                        "internalType": "address",
                        "name": "recipient",
                        "type": "address"
                    },
                    {
                        "internalType": "uint128",
                        "name": "amount",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint256",
                        "name": "maxPayed",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "minAcquired",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deadline",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct Swap.SwapParams",
                "name": "swapParams",
                "type": "tuple"
            }
        ],
        "name": "swapY2X",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [
            {
                "components": [
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
                        "name": "boundaryPt",
                        "type": "int24"
                    },
                    {
                        "internalType": "address",
                        "name": "recipient",
                        "type": "address"
                    },
                    {
                        "internalType": "uint128",
                        "name": "amount",
                        "type": "uint128"
                    },
                    {
                        "internalType": "uint256",
                        "name": "maxPayed",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "minAcquired",
                        "type": "uint256"
                    },
                    {
                        "internalType": "uint256",
                        "name": "deadline",
                        "type": "uint256"
                    }
                ],
                "internalType": "struct Swap.SwapParams",
                "name": "swapParams",
                "type": "tuple"
            }
        ],
        "name": "swapY2XDesireX",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "stateMutability": "payable",
        "type": "receive"
    }
]
