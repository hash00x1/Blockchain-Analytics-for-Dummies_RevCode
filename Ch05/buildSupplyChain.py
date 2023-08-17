import json
import uuid
from web3 import Web3
from datetime import datetime

ganache_url = "ADD LOCALHOST"
web3 = Web3(Web3.HTTPProvider(ganache_url))

web3.eth.defaultAccount = web3.eth.accounts[0]

with open('SupplyChain.abi') as f:
    abi = json.load(f)

# supplyChain contract address - convert to checksum address
address = web3.toChecksumAddress('ADDRESS')

# Initialize supplyChain contract
contract = web3.eth.contract(address=address, abi=abi)

# Create 3 manufacturer participants (A, B, C), 2 supplier participants (D, E), and 2 consumer participants (F, G)
fileHandle = open('participants.csv', 'r')

header = fileHandle.readline()   # skip the first line (field name list) 
for line in fileHandle:
    if line.endswith('\n'):
        line = line[:-1]
    print('Adding: ',line)
    fields = line.split(',')
    vUUID = str(uuid.uuid4())
    tx_hash = contract.functions.addParticipant(vUUID,fields[0],fields[1],fields[2],web3.eth.accounts[int(fields[3])]).transact()
fileHandle.close()

# Wait for last transaction to be mined
web3.eth.waitForTransactionReceipt(tx_hash)

# Display the participants we just created
participantCount = contract.functions.participant_id().call()
for i in range (0, participantCount):
    print ('participant(',i,')',contract.functions.participants(i).call())
    #print(contract.functions.getParticipant(i).call())

# Create 150 products 
fileHandle = open('products.csv', 'r')

header = fileHandle.readline()   # skip the first line (field name list)
for line in fileHandle:
    if line.endswith('\n'):
        line = line[:-1]
    fields = line.split(',')
    print('Adding: ',line)
    dt = datetime(int(fields[6]),int(fields[7]),int(fields[8]),int(fields[9]),int(fields[10]),int(fields[11]),int(fields[12]))
    timestamp = int(datetime.timestamp(dt))
    vUUID = str(uuid.uuid4())
    tx_hash = contract.functions.addProduct(vUUID,int(fields[0]),fields[1],fields[2],fields[3],int(fields[4]),int(fields[5]),timestamp).transact({'from': web3.eth.accounts[int(fields[0])]})
fileHandle.close()

# Wait for last transaction to be mined
web3.eth.waitForTransactionReceipt(tx_hash)

# Display the products we just created
productCount = contract.functions.product_id().call()
for i in range (0, productCount):
    print ('product(',i,')',contract.functions.products(i).call())
    #print(contract.functions.getProduct(i).call())

# Move products along supply chain: Manufacturer=> Supplier=> Supplier=> Consumer
fileHandle = open('transfers.csv', 'r')

header = fileHandle.readline()   # skip the first line (field name list)
for line in fileHandle:
    if line.endswith('\n'):
        line = line[:-1]
    fields = line.split(',')
    dt = datetime(int(fields[6]),int(fields[7]),int(fields[8]),int(fields[9]),int(fields[10]),int(fields[11]),int(fields[12]))
    timestamp = int(datetime.timestamp(dt))
    print('Adding: ',line)
    tx_hash = contract.functions.newOwner(int(fields[0]),int(fields[1]),int(fields[2]),int(fields[3]),int(fields[4]),int(fields[5]),timestamp).transact({'from': web3.eth.accounts[int(fields[1])]})
    web3.eth.waitForTransactionReceipt(tx_hash)
fileHandle.close()

# Wait for last transaction to be mined
# web3.eth.waitForTransactionReceipt(tx_hash)

# Display the supply chain tracks we just created
ownershipCount = contract.functions.owner_id().call()
for i in range (0, ownershipCount):
    print ('ownership(',i,')',contract.functions.ownerships(i).call())
    #print(contract.functions.getProvenance(i).call())

# Display the provenance of each product
for i in range (0, productCount):
    print ('productProvinance(',i,')',contract.functions.getProvenance(i).call())
