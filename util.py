import time
from solc import compile_source


def compile_source_file(file_path):
   with open(file_path, 'r') as f:
      source = f.read()
   return compile_source(source)


def deploy_contract(w3, contract_interface):
    new_contract = w3.eth.contract(
        abi=contract_interface['abi'],
        bytecode=contract_interface['bin'])
    tx_hash = new_contract.constructor(1,"https://example.com",'0x2B5AD5c4795c026514f8317c7a215E218DcCD6cF',50).transact()
    address = w3.eth.getTransactionReceipt(tx_hash)['contractAddress']
    return address


def wait_for_receipt(w3, tx_hash, poll_interval):
   while True:
       tx_receipt = w3.eth.getTransactionReceipt(tx_hash)
       if tx_receipt:
         return tx_receipt
       time.sleep(poll_interval)


def search_contributor(contributors_list, contributor_address):
    for index, val in enumerate(contributors_list):
        if val['address'] == contributor_address:
            return index
    else:
        return -1

