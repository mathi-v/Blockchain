from flask import Flask, jsonify, request
from blockchain import Block, Blockchain, Transaction
import requests
import json

app = Flask(__name__)
blockchain = Blockchain()
peers = set()

@app.route('/mine', methods=['GET'])
def mine_block():
    miner_address = request.args.get('miner_address')
    blockchain.mine_pending_transactions(miner_address)
    announce_new_block(blockchain.chain[-1])
    return jsonify({"message": "Block mined successfully!"}), 200

@app.route('/transactions/new', methods=['POST'])
def add_transaction():
    tx_data = request.get_json()
    transaction = Transaction(tx_data['sender'], tx_data['recipient'], tx_data['amount'])
    blockchain.add_transaction(transaction)
    announce_new_transaction(tx_data)
    return jsonify({"message": "Transaction added!"}), 201

@app.route('/transaction/new', methods=['POST'])
def receive_transaction():
    tx_data = request.get_json()
    transaction = Transaction(tx_data['sender'], tx_data['recipient'], tx_data['amount'])
    blockchain.add_transaction(transaction)
    return jsonify({"message": "Transaction received!"}), 200

@app.route('/block/new', methods=['POST'])
def receive_block():
    block_data = request.get_json()
    block = Block(
        block_data['index'],
        block_data['previous_hash'],
        block_data['timestamp'],
        [Transaction(tx['sender'], tx['recipient'], tx['amount']) for tx in block_data['transactions']],
        block_data['nonce']
    )
    if blockchain.is_valid_chain(block):
        blockchain.chain.append(block)
        return jsonify({"message": "Block accepted!"}), 200
    else:
        return jsonify({"message": "Block rejected!"}), 400

@app.route('/chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            "index": block.index,
            "timestamp": block.timestamp,
            "transactions": [tx.to_dict() for tx in block.transactions],
            "previous_hash": block.previous_hash,
            "hash": block.hash,
            "nonce": block.nonce
        })
    return jsonify(chain_data), 200

@app.route('/add_peer', methods=['POST'])
def add_peer():
    peer = request.get_json().get("peer")
    secret = request.get_json().get("secret")
    
    if secret == "my_secret" and peer:
        peers.add(peer)
        response = {"message": f"Peer {peer} added successfully!"}
    else:
        response = {"message": "Invalid peer or authentication failed."}
    return jsonify(response), 200



@app.route('/balance/<address>', methods=['GET'])
def get_balance(address):
    balance = blockchain.get_balance(address)
    return jsonify({"address": address, "balance": balance}), 200


@app.route('/balances', methods=['GET'])
def get_all_balances():
    all_balances = blockchain.get_all_balances()
    return jsonify(all_balances), 200


@app.route('/peers', methods=['GET'])
def get_peers():
    return jsonify(list(peers)), 200

@app.route('/pending_transactions', methods=['GET'])
def get_pending_transactions():
    pending_tx_data = [tx.to_dict() for tx in blockchain.pending_transactions]
    return jsonify(pending_tx_data), 200

@app.route('/consensus', methods=['GET'])
def consensus():
    replaced = blockchain.resolve_conflicts()
    if replaced:
        response = {"message": "Chain was replaced with the longest one."}
    else:
        response = {"message": "Chain is already the longest."}
    return jsonify(response), 200

def announce_new_transaction(transaction):
    for peer in peers:
        try:
            requests.post(f"{peer}/transaction/new", json=transaction)
        except requests.exceptions.RequestException:
            pass

def announce_new_block(block):
    block_data = {
        "index": block.index,
        "previous_hash": block.previous_hash,
        "timestamp": block.timestamp,
        "transactions": [tx.to_dict() for tx in block.transactions],
        "nonce": block.nonce,
        "hash": block.hash
    }
    for peer in peers:
        try:
            requests.post(f"{peer}/block/new", json=block_data)
        except requests.exceptions.RequestException:
            pass

if __name__ == '__main__':
    port = int(input("Enter port number: "))
    app.run(host='127.0.0.1', port=port)  # HTTPS enabled
