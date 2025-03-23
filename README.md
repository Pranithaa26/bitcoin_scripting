# **Bitcoin Scripting Assignment (CS 216-Introduction to blockchain)**

## Team Details
Team name : Hashers

**Team Members** **Details :**

Komma Pranitha - 230001040 

vanka Abhinayasri -230003082

Janagam Akhila - 230041012

## Objective :

The objective of this assignment is to create and validate Bitcoin transactions using:

- **Legacy Address Transactions (P2PKH)**
- **SegWit Transactions (P2SH-P2WPKH)**

We achieve this by interacting with `bitcoind`, creating transactions, analyzing scripts, and comparing transaction sizes.

## Repository Structure :


📂 bitcoin_scripting_project
 ├── 📁 src/                         # Source code
 │    ├── legacy_transaction.py       # Code for legacy transactions (P2PKH)
 │    ├── segwit_transaction.py       # Code for SegWit transactions (P2SH-P2WPKH)
                 
 ├── README.md                       # This file
                
 ├── report.pdf                       # Final report (PDF)
 ├── bitcoin.conf                     # Configuration file for bitcoind

## Prerequisites :

Before running the scripts, ensure the following are installed:

1. **Bitcoin Core (bitcoind)** - To interact with the Bitcoin network.
2. **Python 3** - For scripting the transactions.
3. **Dependencies**:
   - Install required libraries using:
     ```sh
     pip install -r requirements.txt
     ```
   - Key Libraries:
     - `python-bitcoinlib`
     - `requests`

## Setting Up `bitcoind`

1. Modify your `bitcoin.conf` file with the following settings:
   ```ini
   regtest=1
   server=1
   rpcuser=your_rpc_user
   rpcpassword=your_rpc_password
   txindex=1
   paytxfee=0.0001
   fallbackfee=0.0002
   mintxfee=0.00001
   txconfirmtarget=6
   ```
2. Start Bitcoin Core in `regtest` mode:
   ```sh
   bitcoind -daemon -conf=bitcoin.conf
   ```
3. Verify connectivity:
   ```sh
   bitcoin-cli getblockchaininfo
   ```

## Assignment Steps

### **1. Legacy Address Transactions (P2PKH)**

#### **Step 1: Setup Environment**

- Install and configure `bitcoind`.
- Ensure `bitcoin.conf` is correctly configured.

#### **Step 2: Create and Fund Wallet**

- Connect to `bitcoind` using RPC.
- Create a new wallet or load an existing one.
- Generate three legacy addresses: **A, B, C**.
- Fund address **A** using `sendtoaddress`.

#### **Step 3: Create and Sign Transactions**

- Create a raw transaction from **A → B**.
- Decode and analyze the raw transaction.
- Sign the transaction using the private key of A.
- Broadcast the transaction to the network.

#### **Step 4: Verify and Repeat**

- Check `listunspent` to find the UTXO for address **B**.
- Use this UTXO as input to create a transaction from **B → C**.
- Repeat the signing and broadcasting process.
- Analyze the decoded transaction structure (ScriptPubKey and ScriptSig).

### **2. SegWit Transactions (P2SH-P2WPKH)**

#### **Step 1: Setup Environment**

- Connect to `bitcoind` and create/load a wallet.

#### **Step 2: Generate SegWit Addresses**

- Generate three SegWit addresses: **A', B', C'**.
- Fund **A'** using `sendtoaddress`.

#### **Step 3: Create and Sign Transactions**

- Create a raw transaction from **A' → B'**.
- Decode and analyze the raw transaction.
- Sign and broadcast the transaction.

#### **Step 4: Verify and Repeat**

- Check `listunspent` for the UTXO from **B'**.
- Use this UTXO to create a transaction from **B' → C'**.
- Repeat the signing, broadcasting, and analysis steps.

### **3. Analysis and Comparison**

- **Compare the transaction sizes** between Legacy (P2PKH) and SegWit (P2SH-P2WPKH).
- **Analyze the challenge-response script** structure.
- **Explain why SegWit transactions are smaller and more efficient**.
- **Use Bitcoin Debugger** to validate transactions and scripts.

## Running the Scripts

### **1. Legacy Address Transactions (P2PKH)**

```sh
python src/legacy_transaction.py
```

### **2. SegWit Transactions (P2SH-P2WPKH)**

```sh
python src/segwit_transaction.py
```

## Expected Output

After executing the scripts, you should see:

- Generated Bitcoin addresses.
- Transaction IDs (`txid`) for A → B and B → C.
- Decoded scripts showing locking/unlocking mechanisms.
- Broadcasted transactions on the Bitcoin Regtest network.

## Troubleshooting

- If `bitcoind` is not running, restart it using:
  ```sh
  bitcoind -daemon -conf=bitcoin.conf
  ```
- If `bitcoin-cli` cannot connect, check the `rpcuser` and `rpcpassword` in `bitcoin.conf`.
- If transactions fail, check wallet balance:
  ```sh
  bitcoin-cli listunspent
  ```




