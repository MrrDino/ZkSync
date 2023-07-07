ROUTER_ABI = [
    {
        "inputs": [
            {
                "internalType": "uint256",
                "name": "amountIn",
                "type": "uint256"
            },
            {
                "internalType": "uint256",
                "name": "amountOutMin",
                "type": "uint256"
            },
            {
                'components': [
                    {
                        'internalType': 'address',
                        'name': 'from',
                        'type': 'address',
                    },
                    {
                        'internalType': 'address',
                        'name': 'to',
                        'type': 'address',
                    },
                    {
                        'internalType': 'bool',
                        'name': 'stable',
                        'type': 'bool',
                    },
                ],
                'internalType': 'struct Router.route[]',
                'name': 'routes',
                'type': 'tuple[]',
            },
            {
                "internalType": "address",
                "name": "to",
                "type": "address"
            },
            {
                "internalType": "uint256",
                "name": "deadline",
                "type": "uint256"
            }
        ],
        "name": "swapExactTokensForETH",
        "outputs": [
            {
                "internalType": "uint256",
                "name": "",
                "type": "uint256"
            }
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'amountOutMin',
                'type': 'uint256',
            },
            {
                'components': [
                    {
                        'internalType': 'address',
                        'name': 'from',
                        'type': 'address',
                    },
                    {
                        'internalType': 'address',
                        'name': 'to',
                        'type': 'address',
                    },
                    {
                        'internalType': 'bool',
                        'name': 'stable',
                        'type': 'bool',
                    },
                ],
                'internalType': 'struct Router.route[]',
                'name': 'routes',
                'type': 'tuple[]',
            },
            {
                'internalType': 'address',
                'name': 'to',
                'type': 'address',
            },
            {
                'internalType': 'uint256',
                'name': 'deadline',
                'type': 'uint256',
            },
        ],
        'name': 'swapExactETHForTokens',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': '',
                'type': 'uint256',
            },
        ],
        'stateMutability': 'payable',
        'type': 'function',
    },
    {
        'inputs': [
            {
                'internalType': 'uint256',
                'name': 'amountIn',
                'type': 'uint256',
            },
            {
                'internalType': 'address',
                'name': 'tokenIn',
                'type': 'address',
            },
            {
                'internalType': 'address',
                'name': 'tokenOut',
                'type': 'address',
            },
        ],
        'name': 'getAmountOut',
        'outputs': [
            {
                'internalType': 'uint256',
                'name': 'amount',
                'type': 'uint256',
            },
            {
                'internalType': 'bool',
                'name': 'stable',
                'type': 'bool',
            },
        ],
        'stateMutability': 'view',
        'type': 'function',
    }
]
