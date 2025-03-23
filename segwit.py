from bitcoinrpc.authproxy import AuthServiceProxy, JSONRPCException
from decimal import Decimal

# 🔗 Connect to Bitcoin Core RPC
rpc_user = "hashers"
rpc_password = "xyz111"
rpc_url = f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443"
rpc_connection = AuthServiceProxy(rpc_url)

try:
    # 1️ Load or Create a Wallet
    wallet_name = "testwallet"
    wallets = rpc_connection.listwallets()

    if wallet_name not in wallets:
        try:
            rpc_connection.loadwallet(wallet_name)
            print(f" Wallet '{wallet_name}' successfully loaded.")
        except JSONRPCException:
            rpc_connection.createwallet(wallet_name)
            print(f" Wallet '{wallet_name}' created successfully.")

    # Switch to the loaded wallet
    rpc_connection = AuthServiceProxy(f"{rpc_url}/wallet/{wallet_name}")

    # 2️ Generate Three P2SH-SegWit Addresses: A', B', C'
    addr_Ap = rpc_connection.getnewaddress("A'", "p2sh-segwit")
    addr_Bp = rpc_connection.getnewaddress("B'", "p2sh-segwit")
    addr_Cp = rpc_connection.getnewaddress("C'", "p2sh-segwit")

    print(f" P2SH-SegWit Address A': {addr_Ap}")
    print(f" P2SH-SegWit Address B': {addr_Bp}")
    print(f" P2SH-SegWit Address C': {addr_Cp}")

    # 3️ Fund Address A' (Mine Blocks + Send BTC)
    rpc_connection.generatetoaddress(101, addr_Ap)  # Mine 101 blocks to unlock funds
    txid_fund = rpc_connection.sendtoaddress(addr_Ap, Decimal("10.0"))  # Send 10 BTC to A'
    print(f" Funded Address A' with 10 BTC: {txid_fund}")

    # 4️ Ensure UTXOs Exist
    rpc_connection.generatetoaddress(1, addr_Cp)  # Mine 1 block to confirm
    utxos = rpc_connection.listunspent(1, 9999999, [addr_Ap])

    if not utxos:
        raise Exception(" No UTXOs found in Address A'! Try mining another block.")

    input_utxo = utxos[0]  # Select the first available UTXO

    # 5️ Create & Broadcast Transaction (A' → B')
    fee = Decimal("0.0001")
    send_amount = Decimal("4.9")
    change_amount = input_utxo["amount"] - send_amount - fee

    if change_amount <= 0:
        raise Exception(" Not enough balance after fees!")

    outputs = {addr_Bp: send_amount, addr_Ap: change_amount}
    raw_tx = rpc_connection.createrawtransaction([{"txid": input_utxo["txid"], "vout": input_utxo["vout"]}], outputs)
    signed_tx = rpc_connection.signrawtransactionwithwallet(raw_tx)

    if not signed_tx["complete"]:
        raise Exception(" Transaction signing failed!")

    txid_broadcast = rpc_connection.sendrawtransaction(signed_tx["hex"])
    print(f" A' → B' Transaction ID: {txid_broadcast}")

    # Print raw and signed transaction hex for debugging
    print(f"Raw Transaction Hex (A' → B'): {raw_tx}")
    print(f"Signed Transaction Hex (A' → B'): {signed_tx['hex']}")

    # 6️ Mine a Block to Confirm Transaction
    rpc_connection.generatetoaddress(1, addr_Cp)

    # 7️ Fetch UTXOs for Address B'
    utxos_B = rpc_connection.listunspent(1, 9999999, [addr_Bp])
    if not utxos_B:
        raise Exception(" No UTXOs found in Address B'! Try mining another block.")

    input_utxo_B = utxos_B[0]  # Select first UTXO

    # 8️ Create & Broadcast Transaction (B' → C')
    send_amount_B = Decimal("4.8")  # Sending slightly less to cover fees
    change_amount_B = input_utxo_B["amount"] - send_amount_B - fee

    outputs_B = {addr_Cp: send_amount_B, addr_Bp: change_amount_B}
    raw_tx_B = rpc_connection.createrawtransaction([{"txid": input_utxo_B["txid"], "vout": input_utxo_B["vout"]}], outputs_B)
    signed_tx_B = rpc_connection.signrawtransactionwithwallet(raw_tx_B)

    if not signed_tx_B["complete"]:
        raise Exception(" Transaction signing failed!")

    txid_broadcast_B = rpc_connection.sendrawtransaction(signed_tx_B["hex"])
    print(f" B' → C' Transaction ID: {txid_broadcast_B}")

    # Print raw and signed transaction hex for debugging
    print(f"Raw Transaction Hex (B' → C'): {raw_tx_B}")
    print(f"Signed Transaction Hex (B' → C'): {signed_tx_B['hex']}")

    # 9️ Decode and Analyze Transactions
    decoded_tx_AtoB = rpc_connection.decoderawtransaction(raw_tx)
    decoded_tx_BtoC = rpc_connection.decoderawtransaction(raw_tx_B)

    print("\n Decoded A' → B' Transaction:")
    print(f"- Transaction ID: {decoded_tx_AtoB['txid']}")
    print(f"- Version: {decoded_tx_AtoB['version']}")
    print(f"- Locktime: {decoded_tx_AtoB['locktime']}")
    print(f"- Outputs: {decoded_tx_AtoB['vout']}")

    print("\n Decoded B' → C' Transaction:")
    print(f"- Transaction ID: {decoded_tx_BtoC['txid']}")
    print(f"- Version: {decoded_tx_BtoC['version']}")
    print(f"- Locktime: {decoded_tx_BtoC['locktime']}")
    print(f"- Outputs: {decoded_tx_BtoC['vout']}")

    # Extract Locking and Unlocking Scripts
    scriptPubKey_B = decoded_tx_AtoB["vout"][0]["scriptPubKey"]["hex"]
    scriptPubKey_C = decoded_tx_BtoC["vout"][0]["scriptPubKey"]["hex"]

    print(f"\n Locking Script (scriptPubKey) for B': {scriptPubKey_B}")
    print(f" Locking Script (scriptPubKey) for C': {scriptPubKey_C}")

    # Extract Unlocking Scripts (scriptSig or witness)
    if "vin" in decoded_tx_BtoC and len(decoded_tx_BtoC["vin"]) > 0:
        vin = decoded_tx_BtoC["vin"][0]
        if "scriptSig" in vin:
            scriptSig_B = vin["scriptSig"]["hex"]
            print(f" Unlocking Script (scriptSig) for B': {scriptSig_B}")
        if "txinwitness" in vin:
            scriptWitness_B = vin["txinwitness"]
            print(f" Witness Data for B': {scriptWitness_B}")

    print("\n Scripts Extracted. You can validate them using Bitcoin Debugger.")

except Exception as e:
    print(f" Error: {e}")
