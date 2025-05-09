from web3 import Web3
import os

# You should set these environment variables or replace with your own endpoints
ETHEREUM_RPC_URL = os.environ.get('ETHEREUM_RPC_URL', 'https://mainnet.infura.io/v3/0c955f398caf48a182d81e3641791f6d')
BSC_RPC_URL = os.environ.get('BSC_RPC_URL', 'https://bsc-dataseed.binance.org/')

w3_eth = Web3(Web3.HTTPProvider(ETHEREUM_RPC_URL))
w3_bsc = Web3(Web3.HTTPProvider(BSC_RPC_URL))

def get_native_balance(address, chain='ethereum'):
    """
    Get native coin balance (ETH or BNB) for the given address.
    """
    if chain == 'ethereum':
        w3 = w3_eth
    elif chain == 'bsc':
        w3 = w3_bsc
    else:
        raise ValueError('Unsupported chain')
    return w3.from_wei(w3.eth.get_balance(address), 'ether')

# Example ERC-20 ABI fragment for balanceOf
ERC20_ABI = [
    {
        "constant": True,
        "inputs": [{"name": "_owner", "type": "address"}],
        "name": "balanceOf",
        "outputs": [{"name": "balance", "type": "uint256"}],
        "type": "function",
    }
]

def get_erc20_balance(address, contract_address, chain='ethereum'):
    """
    Get ERC-20/BEP-20 token balance for the given address and contract.
    """
    print(f"DEBUG: Checking balance for address {address} on {chain} with contract {contract_address}")
    if chain == 'ethereum':
        w3 = w3_eth
    elif chain == 'bsc':
        w3 = w3_bsc
    else:
        raise ValueError('Unsupported chain')
    try:
        contract = w3.eth.contract(address=Web3.to_checksum_address(contract_address), abi=ERC20_ABI)
        balance = contract.functions.balanceOf(Web3.to_checksum_address(address)).call()
        return balance / (10 ** 18)  # Most tokens use 18 decimals
    except Exception as e:
        print(f"ERROR: Could not fetch token balance. Reason: {e}")
        return 0.0
