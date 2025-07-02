# Spend the hashlock leaf of a 4-leaf Taproot address via Script Path - Hashlock - Script1
# Author: Aaron Zhang
# Sucess TxID: 1ba4835fca1c94e7eb0016ce37c6de2545d07d84a97436f8db999f33a6fd6845
# Environment: Python 3.11, bitcoinutils (latest), Testnet

from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput
from bitcoinutils.keys import PrivateKey
import hashlib
import os, sys
import configparser
import requests

# Read config from wallet_info.conf
conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wallet_info.conf")
conf.read(conf_file)

def main():
    setup('testnet')

    # Alice's internal private key (for Taproot address)
    alice_priv = PrivateKey(conf.get("default", "alice_private_key_wif"))
    alice_pub = alice_priv.get_public_key()
    print(f"Alice's pubkey: {alice_pub.to_hex()}, len: {len(alice_pub.to_hex())}")

    # Bob's private key (for other leaves, not used here)
    bob_priv = PrivateKey(conf.get("default", "bob_private_key_wif"))
    bob_pub = bob_priv.get_public_key()
    print(f"Bob's pubkey: {bob_pub.to_hex()}, len: {len(bob_pub.to_hex())}")

    # Script 1: hashlock (SHA256(preimage) == hash(helloworld))
    preimage = "helloworld"
    preimage_hex = preimage.encode('utf-8').hex()
    hash1 = hashlib.sha256(preimage.encode('utf-8')).hexdigest()
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
    relative_blocks = 2
    from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
    from bitcoinutils.transactions import Sequence
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

    # Build Merkle Tree (must match the address construction)
    tree = [[script1, script2], [script3, script4]]
    taproot_address = alice_pub.get_taproot_address(tree)
    print(f"Taproot address: {taproot_address.to_string()}")

    # UTXO info (fill in your actual UTXO)
    commit_txid = "245563c5aa4c6d32fc34eed2f182b5ed76892d13370f067dc56f34616b66c468"
    vout = 0
    input_amount = 1200  # in satoshis
    output_amount = 666 # in satoshis
    # fee = 200            # in satoshis

    # Spend via Script Path (hashlock leaf, index 0)
    txin = TxInput(commit_txid, vout)
    txout = TxOutput(output_amount, alice_pub.get_taproot_address().to_script_pub_key())
    tx = Transaction([txin], [txout], has_segwit=True)

    # Control block for script1 (index 0 in the tree)
    cb = ControlBlock(alice_pub, tree, 0, is_odd=taproot_address.is_odd())

    # Witness: [preimage, script, control_block]
    tx.witnesses.append(
        TxWitnessInput([
            preimage_hex,
            script1.to_hex(),
            cb.to_hex()
        ])
    )

    print(f"Script Path spending (hashlock leaf):")
    print(f"Input: {commit_txid}:{vout}")
    print(f"Output: {alice_pub.get_taproot_address().to_string()} ({output_amount} sats)")
    print(f"TxId: {tx.get_txid()}")
    print(f"Raw Tx: {tx.serialize()}")

    # Broadcast (optional)
    print("\nBroadcasting transaction...")
    mempool_api = "https://mempool.space/testnet/api/tx"
    try:
        response = requests.post(mempool_api, data=tx.serialize())
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