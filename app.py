import json, datetime

from flask import Flask, request

from config import DevelopmentConfig
from models import *
from util import *

from web3 import Web3,EthereumTesterProvider


# Flask application
app = Flask(__name__)
app.config.from_object(DevelopmentConfig())

# DB initialization
db.init_app(app)

# Blockchain Network
w3 = Web3(EthereumTesterProvider())

# Deploy contract on blockchain Network
compiled_sol = compile_source_file('docs/crowd_funding.sol')
contract_id, contract_interface = compiled_sol.popitem()
address = deploy_contract(w3, contract_interface)
print("Deployed {0} to: {1}\n".format(contract_id, address))
crowd_funding_contract = w3.eth.contract(
   address=address,
   abi=contract_interface['abi'])

contributors_list = []


@app.route('/')
def index():
    creator = crowd_funding_contract.functions.getCreator().call()
    receiver = crowd_funding_contract.functions.getReceiver().call()
    target = crowd_funding_contract.functions.getTarget().call()
    expiry_date = datetime.datetime.fromtimestamp(crowd_funding_contract.functions.getExpiry().call()).strftime('%c')
    current_state = crowd_funding_contract.functions.getState().call()
    bal = crowd_funding_contract.functions.getBalance().call()
    return json.dumps({"Project":"Crowd Funding", "balance":bal, "target": target, "expiry_date":expiry_date,\
                       "current_state":current_state, "receiver":receiver, "creator":creator })


@app.route('/donate', methods=['POST'])
def contribute():
    block_data = request.get_json()
    tx_hash = crowd_funding_contract.functions.contribute(block_data['address'], block_data['amount']).transact()
    receipt = wait_for_receipt(w3, tx_hash, 1)
    contributors_list.append({'address': block_data['address'], 'amount': block_data['amount']})
    return json.dumps({"msg":"Sucessfully donated", "transaction_hash": str(receipt['transactionHash']), \
                       "transaction_index": receipt['transactionIndex'], "block_hash": str(receipt['blockHash']), \
                       "block_number": receipt['blockNumber'], "gas_used": receipt['gasUsed']})


@app.route('/contributors')
def display_contributors():
    return json.dumps({"contributors": contributors_list})


@app.route('/refund', methods=['POST'])
def refund():
    block_data = request.get_json()
    result_index = search_contributor(contributors_list, block_data['address'])
    if result_index != -1:
        tx_hash = crowd_funding_contract.functions.getRefund(block_data['address']).transact()
        receipt = wait_for_receipt(w3, tx_hash, 1)
        contributors_list.pop(result_index)
        return json.dumps({"msg":"Sucessfully refund.", "transaction_hash": str(receipt['transactionHash']), \
                           "transaction_index": receipt['transactionIndex'], "block_hash": str(receipt['blockHash']), \
                           "block_number": receipt['blockNumber'], "gas_used": receipt['gasUsed']})
    else:
        return json.dumps({"msg":"No such address is available in contributors list."})


@app.route('/payout')
def payout():
    target = crowd_funding_contract.functions.getTarget().call()
    bal = crowd_funding_contract.functions.getBalance().call()
    if bal < target:
        return json.dumps({"msg": "Fund is not colleted till target amount."})
    else:
        tx_hash = crowd_funding_contract.functions.payOut().transact()
        receipt = wait_for_receipt(w3, tx_hash, 1)
        return json.dumps({"msg":"Payout sucessfully.", "transaction_hash": str(receipt['transactionHash']), \
                           "transaction_index": receipt['transactionIndex'], "block_hash": str(receipt['blockHash']), \
                           "block_number": receipt['blockNumber'], "gas_used": receipt['gasUsed']})


@app.route('/remove')
def delete_contract():
    tx_hash = crowd_funding_contract.functions.removeContract().transact()
    receipt = wait_for_receipt(w3, tx_hash, 1)
    return json.dumps({"msg":"Contract is deleted sucessfully.", "transaction_hash": str(receipt['transactionHash']), \
                       "transaction_index": receipt['transactionIndex'], "block_hash": str(receipt['blockHash']), \
                       "block_number": receipt['blockNumber'], "gas_used": receipt['gasUsed']})


if __name__ == '__main__':
    app.run()