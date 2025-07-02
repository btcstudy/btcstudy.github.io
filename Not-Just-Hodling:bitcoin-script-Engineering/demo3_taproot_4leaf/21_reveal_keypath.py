# Spend the 4-leaf Taproot address (from 17_4leaf_scripts_addr.py) via Key Path
# Author: Aaron Zhang
# Sucess TxID: 1e518aa540bc770df549ec9836d89783ca19fc79b84e7407a882cbe9e95600da
# Environment: Python 3.11, bitcoinutils (latest), Testnet

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput, Sequence
from bitcoinutils.keys import PrivateKey
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
import hashlib
import os, sys
import requests
import configparser



conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wallet_info.conf")
conf.read(conf_file)

alice_wif = conf.get("default", "alice_private_key_wif")
bob_wif = conf.get("default", "bob_private_key_wif")

def main():
    setup('testnet')
    
    # Alice's internal private key (for Taproot address)
    alice_priv = PrivateKey(alice_wif)
    alice_pub = alice_priv.get_public_key()
    print(f"Alice's pubkey: {alice_pub.to_hex()}, len: {len(alice_pub.to_hex())}")

    # Bob's private key (for multisig and CSV timelock script path)
    bob_priv = PrivateKey(bob_wif)
    bob_pub = bob_priv.get_public_key()    
    print(f"Bob's pubkey: {bob_pub.to_hex()}, len: {len(bob_pub.to_hex())}")

    # Rebuild the four leaf scripts from 17_4leaf_scripts_addr.py
    # Script 1: hashlock (SHA256(preimage) == hash(helloworld))
    hash1 = hashlib.sha256(b"helloworld").hexdigest()
    script1 = Script(['OP_SHA256', hash1, 'OP_EQUALVERIFY', 'OP_TRUE'])
    print(f"1st script hex: {script1.to_hex()}")

    # Script 2: 2-of-2 multisig (tapscript style)
    script2 = Script([
        "OP_0",
        alice_pub.to_x_only_hex(),
        "OP_CHECKSIGADD",
        bob_pub.to_x_only_hex(),
        "OP_CHECKSIGADD",
        "OP_2", 
        "OP_EQUAL"
    ])
    print(f"2nd script hex: {script2.to_hex()}")

    # Script 3: CSV timelock
    relative_blocks = 2 # 10 blocks, about 2 hours
    seq = Sequence(TYPE_RELATIVE_TIMELOCK, relative_blocks)
    script3 = Script([
        seq.for_script(),
        "OP_CHECKSEQUENCEVERIFY",
        "OP_DROP",
        bob_pub.to_x_only_hex(),
        "OP_CHECKSIG"
    ])
    print(f"3rd script hex: {script3.to_hex()}")

    # Script 4: Bob's siglock
    script4 = Script([
        bob_pub.to_x_only_hex(),
        "OP_CHECKSIG"
    ])
    print(f"4th script hex: {script4.to_hex()}")

    # Build Merkle Tree
    tree = [[script1, script2], [script3, script4]]
    
    taproot_address = alice_pub.get_taproot_address(tree)
    print(f"=== Alice Key Path Spend ===")
    print(f"Taproot address: {taproot_address.to_string()}")
    print(f"Alice WIF: {alice_priv.to_wif()}")
    print(f"Alice pubkey: {alice_pub.to_hex()}")
    print(f"Spend method: Key Path (most private)")

 
    commit_txid = "42a9796a91cf971093b35685db9cb1a164fb5402aa7e2541ea7693acc1923059"
    vout = 0  # UTXO vout
    input_amount = 2000  # UTXO amount (satoshis)
    output_amount = 888  # Amount to send (satoshis)

    # Build transaction
    txin = TxInput(commit_txid, vout)
    txout = TxOutput(output_amount, alice_pub.get_taproot_address().to_script_pub_key())
    tx = Transaction([txin], [txout], has_segwit=True)
    
    print(f"\n=== Transaction Construction ===")
    print(f"Input: {commit_txid}:{vout}")
    print(f"Output: {alice_pub.get_taproot_address().to_string()}")
    
    # Alice signs via Key Path
    sig = alice_priv.sign_taproot_input(
        tx,
        0,
        [taproot_address.to_script_pub_key()],  # input scriptPubKey
        [input_amount],            # input amount
        script_path=False,                      # Key Path spend
        tapleaf_scripts=tree               # full script tree (for tweak calculation)
    )
    print(f"Alice signature: {sig}")
    tx.witnesses.append(TxWitnessInput([sig]))
    print(f"TxId: {tx.get_txid()}")
    print("\nTxwId:", tx.get_wtxid())
    print(f"Transaction size: {tx.get_size()} bytes")
    print(f"Virtual size: {tx.get_vsize()} vbytes")
    signed_tx = tx.serialize()
    print(f"Raw Tx: {signed_tx}")

    # Broadcast transaction (optional)
    print("\nBroadcasting transaction...")
    mempool_api = "https://mempool.space/testnet/api/tx"
    try:
        response = requests.post(mempool_api, data=signed_tx)
        if response.status_code == 200:
            txid = response.text
            print(f"Broadcast success!")
            print(f"TxID: {txid}")
            print(f"View: https://mempool.space/testnet/tx/{txid}")
        else:
            print(f"Broadcast failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")   

if __name__ == "__main__":
    main() 