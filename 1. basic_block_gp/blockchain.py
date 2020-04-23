import hashlib
import json
from time import time
from uuid import uuid4

from flask import Flask, jsonify, request


class Blockchain(object):
    def __init__(self):
        self.chain = []
        # transactions are like purchases like derrick bought 5 cd's, amount, cost ...
        self.current_transactions = []

        # Create the genesis block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):

        if len(self.chain) > 0:
            block_string = json.dumps(self.last_block, sort_keys=True)
            guess = f'{block_string}{proof}'.encode()
            current_hash = hashlib.sha256(guess).hexdigest()
        else:
            current_hash = ""

        block = {
            # TODO
            "index": len(self.chain) + 1,
            "timestamp": time(),
            "transactions": self.current_transactions,
            "proof": proof,
            "previous_hash": previous_hash or self.hash(self.chain[-1])
        }

        # Reset the current list of transactions
        self.current_transactions = []

        # Append the block to chain
        self.chain.append(block)

        # Return the new block
        return block

    def hash(self, block):
        # Stringify Object
        # object needs to be in order to stay deterministic
        stringified_object = json.dumps(block, sort_keys=True)

        # Turn stringified object into a byte string to be hashable
        byte_string = stringified_object.encode()

        # Hash using sha256 <- sha256 only takes byte strings
        raw_hash = hashlib.sha256(byte_string)

        # turn hash object into hexadecimal string that is easier to read and use
        hex_hash = raw_hash.hexdigest()

        # Return the hashed block string in hexadecimal format
        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    def proof_of_work(self, block=None):
        """
        in our implementation we are looking for an integer as proof
        stringify the block, and increment integer,
            checking as you increment to see if it works
        :return: A valid proof for the provided block
        """
        # block aka blockchain aka last block on chain stringified
        block_string = json.dumps(self.last_block, sort_keys=True)

        proof = 0

        while self.valid_proof(block_string, proof) is False:
            proof += 1

        # return proof
        return proof

    @staticmethod
    def valid_proof(block_string, proof):
        """
        Validates the Proof:  Does hash(block_string, proof) contain 3 leading zeroes?
        :param block_string: <string> The stringified block
        :param proof: <int?> value when combined with stringified previous block
            results in a hash that has 3 leading zeroes.
        """
        # Concatenate block string with proof and encode to byte string
        guess = f'{block_string}{proof}'.encode()

        # hash using sha256
        guess_hash = hashlib.sha256(guess).hexdigest()

        leading_three = guess_hash[:3]

        # return True or False
        return leading_three == '000'


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['GET'])
def mine():
    # Run the proof of work algorithm to get the next proof
    proof = blockchain.proof_of_work()

    # Forge the new Block by adding it to the chain with the proof
    new_block = blockchain.new_block(proof)

    response = {
        'message': "New Block Forged",
        'index': new_block['index'],
        'transactions': new_block['transactions'],
        'proof': new_block['proof'],
        'previous_hash': new_block['previous_hash']
    }

    return jsonify(response), 200


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        'length': len(blockchain.chain),
        'chain': blockchain.chain
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
