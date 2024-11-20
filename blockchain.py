import hashlib
import json
import time
import requests

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }

class Block:
    def __init__(self, index, previous_hash, timestamp, transactions, nonce=0):
        self.index = index
        self.previous_hash = previous_hash
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = f"{self.index}{self.previous_hash}{self.timestamp}{json.dumps([tx.to_dict() for tx in self.transactions])}{self.nonce}"
        return hashlib.sha256(block_string.encode()).hexdigest()
    
    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]
        self.difficulty = 4
        self.pending_transactions = []
        self.mining_reward = 100
        self.peers = set()  # Set to store unique peers

        # Adding predefined peers
        self.add_peer("http://127.0.0.1:8081")
        self.add_peer("http://127.0.0.1:8082")
        self.add_peer("http://127.0.0.1:8083")
        self.add_peer("http://127.0.0.1:8084")

    def create_genesis_block(self):
        return Block(0, "0", time.time(), [], 0)

    def get_latest_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        if transaction.sender and transaction.recipient and transaction.amount > 0:
            self.pending_transactions.append(transaction)
        else:
            raise ValueError("Invalid transaction data")

    def mine_pending_transactions(self, mining_reward_address):
        new_block = Block(len(self.chain), self.get_latest_block().hash, time.time(), self.pending_transactions)
        new_block.mine_block(self.difficulty)

        self.chain.append(new_block)
        self.pending_transactions = [Transaction("Network", mining_reward_address, self.mining_reward)]

    def is_valid_chain(self, chain):
        for i in range(1, len(chain)):
            previous_block = chain[i - 1]
            current_block = chain[i]
            if current_block.previous_hash != previous_block.hash:
                return False
            if current_block.hash != current_block.calculate_hash():
                return False
        return True

    def resolve_conflicts(self):
        new_chain = None
        max_length = len(self.chain)

        for peer in self.peers:
            try:
                response = requests.get(f'{peer}/chain')
                if response.status_code == 200:
                    # Assuming the response is a JSON object containing 'length' and 'chain'
                    data = response.json()  # This is now assumed to be a dictionary
                    if isinstance(data, dict):  # Check if the response is a dictionary
                        length = data.get('length', 0)
                        chain = data.get('chain', [])
                        if length > max_length and self.is_valid_chain(chain):
                            max_length = length
                            new_chain = chain
            except requests.exceptions.RequestException:
                continue

        if new_chain:
            self.chain = [Block(**block) for block in new_chain]
            return True
        return False


    

    def add_peer(self, peer):
        """Add a peer to the network."""
        self.peers.add(peer)
        
    def get_peers(self):
        """Get the list of all known peers."""
        return list(self.peers)
