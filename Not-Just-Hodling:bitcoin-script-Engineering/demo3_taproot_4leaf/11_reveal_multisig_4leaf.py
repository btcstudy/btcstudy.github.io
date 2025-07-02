# Spend the multisig leaf of a 4-leaf Taproot address via Script Path - Multisig - Script2
# Author: Aaron Zhang
# Sucess TxID: 1951a3be0f05df377b1789223f6da66ed39c781aaf39ace0bf98c3beb7e604a1
# Environment: Python 3.11, bitcoinutils (latest), Testnet

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, TxWitnessInput, Sequence
from bitcoinutils.utils import to_satoshis, ControlBlock
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
import hashlib
import os, sys
import configparser
import requests

conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wallet_info.conf")
conf.read(conf_file)

def main():
    setup('testnet')

    # Alice's internal private key (for Taproot address)
    alice_priv = PrivateKey(conf.get("default", "alice_private_key_wif"))
    alice_pub = alice_priv.get_public_key()
    print(f"Alice's pubkey: {alice_pub.to_hex()}, len: {len(alice_pub.to_hex())}")

    # Bob's private key (for multisig and CSV timelock script path)
    bob_priv = PrivateKey(conf.get("default", "bob_private_key_wif"))
    bob_pub = bob_priv.get_public_key()    
    print(f"Bob's pubkey: {bob_pub.to_hex()}, len: {len(bob_pub.to_hex())}")

    # Rebuild script tree
    # Script 1: hashlock (SHA256(preimage) == hash(hellojason))
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
    relative_blocks = 2
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

    # UTXO info
    commit_txid = "1ed5a3e97a6d3bc0493acc2aac15011cd99000b52e932724766c3d277d76daac" 
    vout = 0
    input_amount = 1400  # in satoshis
    output_amount = 668

    # Build transaction
    txin = TxInput(commit_txid, vout)
    txout = TxOutput(output_amount, alice_pub.get_taproot_address().to_script_pub_key())
    tx = Transaction([txin], [txout], has_segwit=True)

    # Control block for script2 (index 1 in the tree)
    cb = ControlBlock(alice_pub, tree, 1, is_odd=taproot_address.is_odd())

    # Signatures for multisig leaf
    sigA = alice_priv.sign_taproot_input(
        tx,
        0,
        [taproot_address.to_script_pub_key()],
        [input_amount],
        script_path=True,
        tapleaf_script=script2,
        tweak=False,
    )
    sigB = bob_priv.sign_taproot_input(
        tx,
        0,
        [taproot_address.to_script_pub_key()],
        [input_amount],
        script_path=True,
        tapleaf_script=script2,
        tweak=False,
    )

    # Witness: [sigB, sigA, script, control_block]
    tx.witnesses.append(
        TxWitnessInput([
            sigB, sigA,
            script2.to_hex(),
            cb.to_hex()
        ])
    )

    print(f"TxId: {tx.get_txid()}")
    print(f"Transaction size: {tx.get_size()} bytes")
    print(f"Virtual size: {tx.get_vsize()} vbytes")
    print(f"Raw Tx: {tx.serialize()}")

    # Broadcast transaction
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

if __name__ == '__main__':
    main()