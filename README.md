# Blockchain
A simple DLT project for my college project

#Working:
run the app using python node.py
Enter the port number: <[enter your port number]

add transaction:  curl -X POST http://127.0.0.1:[port]/transactions/new -H "Content-Type: application/json" -d "{\"sender\": \"address\", \"recipient\": \"address\", \"amount\": [amount]}"

mine: curl -X GET "http://127.0.0.1:[port]/mine?miner_address=Miner123"

blockchain: curl -X GET http://127.0.0.1:[port]/chain

check- balances : curl -X GET http://127.0.0.1:[port]/balance/
curl -X GET http://127.0.0.1:[port]/balance/
curl -X GET http://127.0.0.1:[port]/balance/

pending transactions : curl http://127.0.0.1:[port]/pending_transactions

add-peer: curl -X POST http://127.0.0.1:[port]/add_peer -H "Content-Type: application/json" -d "
{\"peer\": \"http://127.0.0.1:[port]\", \"secret\": \"my_secret\"}"

#Actual_Working:
PoW used = Longest Chain;
mining is done;
no complex Smart Contract is used as the project is meant to be kept simple;
Sha-256 is used to calculate the hash for the block.
The miner is rewared with an arbitrary value of 100 for mining;
simply, the peers are availed with balances of 100, in actual implementation of the project we can improvise the system.


