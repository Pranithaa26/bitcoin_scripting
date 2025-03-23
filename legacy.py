from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal
import time

# RPC Connection Setup
rpc_user = "hashers"
rpc_password = "xyz111"
rpc_url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443"
rpc_connection = AuthServiceProxy(rpc_url)

# Check RPC connection
try:
    blockchain_info = rpc_connection.getblockchaininfo()
    print(f"✅ Successfully connected to Bitcoin Core RPC\nChain: {blockchain_info['chain']}, Blocks: {blockchain_info['blocks']}")
except Exception as e:
    print(f"❌ RPC connection failed: {e}")
    exit()

# Wallet setup
wallet_name = "legacy_wallet"
wallets = rpc_connection.listwallets()
if wallet_name not in wallets:
    try:
        print(f"🆕 Creating new wallet: {wallet_name}")
        rpc_connection.createwallet(wallet_name)
    except JSONRPCException as e:
        if e.error["code"] == -4:  # Wallet already exists
            print(f"⚠ Wallet '{wallet_name}' already exists. Loading instead.")
    rpc_connection.loadwallet(wallet_name)
else:
    print(f"⚡ Wallet '{wallet_name}' is already loaded.")

# Generate three legacy (P2PKH) addresses
addr_A = rpc_connection.getnewaddress("A", "legacy")
addr_B = rpc_connection.getnewaddress("B", "legacy")
addr_C = rpc_connection.getnewaddress("C", "legacy")

print(f"\n📌 Generated Legacy Addresses:\n- Address A: {addr_A}\n- Address B: {addr_B}\n- Address C: {addr_C}")

# Check and Fund Address A
utxos = rpc_connection.listunspent()
if not utxos:
    print("\n🚀 Generating blocks and funding Address A...")
    rpc_connection.generatetoaddress(101, addr_A)
    time.sleep(2)  # Wait for processing

# List UTXOs again
utxos = rpc_connection.listunspent()
if not utxos:
    print("❌ No UTXOs found! Funding failed. Exiting...")
    exit()

# Get largest available UTXO
utxo = max(utxos, key=lambda x: x['amount'])

# Ensure enough balance
amount_to_send = Decimal(min(utxo['amount'], 4.9))  # Convert to Decimal
change_amount = utxo['amount'] - amount_to_send - Decimal("0.0001")  # Ensure Decimal arithmetic
change_address = rpc_connection.getrawchangeaddress()

# Create transaction from A → B
print("\n🔄 Creating transaction from Address A → Address B...")
raw_tx = rpc_connection.createrawtransaction(
    [{"txid": utxo['txid'], "vout": utxo['vout']}],
    {
        addr_B: float(amount_to_send),  # Convert to float only for API call
        change_address: float(change_amount)
    }
)

print("\n📜 Raw Transaction (A → B):")
print(f"{raw_tx}")

signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)
print("\n📜 Signed Transaction (A → B):")
print(f"{signed_tx['hex']}")

tx_id = rpc_connection.sendrawtransaction(signed_tx['hex'])
print(f"✅ Transaction A → B broadcasted successfully! TX ID: {tx_id}")

# Wait for confirmation
time.sleep(2)

# Check UTXOs after first transaction
utxos = rpc_connection.listunspent()
if len(utxos) < 1:
    print("❌ No UTXOs available for the second transaction! Exiting...")
    exit()

# Create transaction from B → C
print("\n🔄 Creating transaction from Address B → Address C...")
utxo_B = max(utxos, key=lambda x: x['amount'])
amount_to_send_BC = Decimal(min(utxo_B['amount'], 4.8))
change_amount_BC = utxo_B['amount'] - amount_to_send_BC - Decimal("0.0001")
change_address_BC = rpc_connection.getrawchangeaddress()

raw_tx_BC = rpc_connection.createrawtransaction(
    [{"txid": utxo_B['txid'], "vout": utxo_B['vout']}],
    {
        addr_C: float(amount_to_send_BC),
        change_address_BC: float(change_amount_BC)
    }
)

print("\n📜 Raw Transaction (B → C):")
print(f"{raw_tx_BC}")

signed_tx_BC = rpc_connection.signrawtransactionwithwallet(raw_tx_BC)
print("\n📜 Signed Transaction (B → C):")
print(f"{signed_tx_BC['hex']}")

tx_id_BC = rpc_connection.sendrawtransaction(signed_tx_BC['hex'])
print(f"✅ Transaction B → C broadcasted successfully! TX ID: {tx_id_BC}")

# Decode and analyze the transaction
decoded_tx = rpc_connection.decoderawtransaction(signed_tx_BC['hex'])
print("\n📜 Decoded Transaction Details (B → C):")
print(f"- Transaction ID: {decoded_tx['txid']}")
print(f"- Version: {decoded_tx['version']}")
print(f"- Locktime: {decoded_tx['locktime']}")

# Extract locking and unlocking scripts
print("\n🔐 Locking Scripts (scriptPubKey):")
for i, vout in enumerate(decoded_tx['vout']):
    print(f"  - Output {i}: {vout['scriptPubKey']['hex']}")

print("\n🔓 Unlocking Script (scriptSig) for Input 0:")
if 'scriptSig' in decoded_tx['vin'][0]:
    print(f"  - ScriptSig: {decoded_tx['vin'][0]['scriptSig']['hex']}")
else:
    print("  - No scriptSig found (likely a SegWit transaction).")

print("\n✅ Scripts extracted successfully. You can validate them using Bitcoin Debugger.")

# Check final UTXO set
final_utxos = rpc_connection.listunspent()
print("\n💰 Final Unspent Outputs (UTXOs):")
for utxo in final_utxos:
    print(f"- TXID: {utxo['txid']}, Vout: {utxo['vout']}, Amount: {utxo['amount']} BTC, Address: {utxo['address']}")
