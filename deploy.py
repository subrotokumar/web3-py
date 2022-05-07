import json

from web3 import Web3
from solcx import compile_standard, install_solc

import os
from dotenv import load_dotenv

load_dotenv()

with open("./SimpleStorage.sol", "r") as file:
    simple_storage_file = file.read()

install_solc("0.6.0")

# Solidity source code
compiled_sol = compile_standard(
    {
        "language": "Solidity",
        "sources": {"SimpleStorage.sol" : { "content" : simple_storage_file }},
        "settings": {
            "outputSelection": {
                "*": {
                    "*": ["abi","metadata","evm.bytecode","evm.sourceMap"]
                }
            }
        }
    },
    solc_version="0.6.0",
)

with open("compiled_code.json","w") as file:
    json.dump(compiled_sol,file)

# get bytecode
bytecode = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["evm"]["bytecode"]["object"]

#  get abi
abi  = compiled_sol["contracts"]["SimpleStorage.sol"]["SimpleStorage"]["abi"]

# for connecting to ganache
w3 = Web3(Web3.HTTPProvider("http://127.0.0.1:8545"))
chain_id = 1337
my_address =  "0xe8661976b7Cf4071e966a883F54a55c2d32A9279"
private_key = os.getenv("PRIVATE_KEY")
# private_key = "0x_________________________________________"

# Create the contract in python
SimpleStorage = w3.eth.contract(abi=abi, bytecode=bytecode)

# Get the latest transaction
nonce = w3.eth.getTransactionCount(my_address)

# Submit the transaction deplays the contract
transaction = SimpleStorage.constructor().buildTransaction({
    "chainId": chain_id,
    "gasPrice": w3.eth.gas_price,
    "from": my_address,
    "nonce": nonce,
})

# Sign the transaction
signed_txn = w3.eth.account.sign_transaction(transaction, private_key=private_key)
print("Deploying Contract!")
# Sent it
tx_hash = w3.eth.send_raw_transaction(signed_txn.rawTransaction)
# Wait for the transaction to be mined, and get transaction receipt
print("Waiting for Transaction to finish...")
tx_receipt=w3.eth.wait_for_transaction_receipt(tx_hash)
print(f"Done! Contract Deployed to {tx_receipt.contractAddress}")


# Working with the contracts
simple_storage = w3.eth.contract(address=tx_receipt.contractAddress, abi=abi)

# Types of Interection : 
# Call -> Simulate making the call and getting a return value
# Transact -> Actually make a state change
print(f"Initial Stored Value {simple_storage.functions.retrieve().call()}")

store_transaction = simple_storage.functions.store(15).buildTransaction({
    "chainId": chain_id,
    "gasPrice": w3.eth.gas_price,
    "from":my_address,
    "nonce":nonce+1,
})
signed_store_txn = w3.eth.account.sign_transaction(
    store_transaction, private_key=private_key
)
signed_store_hash = w3.eth.send_raw_transaction(signed_store_txn.rawTransaction)
tx_receipt = w3.eth.wait_for_transaction_receipt(signed_store_hash)

print(simple_storage.functions.retrieve().call())