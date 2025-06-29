from bitcoinutils.setup import setup
from bitcoinutils.utils import to_satoshis
from bitcoinutils.transactions import Transaction, TxInput, TxOutput, Sequence
from bitcoinutils.keys import P2pkhAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
import os, sys
import configparser
import requests

# Read config file and get private key
conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)

def main():
    setup("testnet")
    relative_blocks = 3
    txid = "8e763d0269963e666949606e84e811a24df9cb525d7c436096b0c8a72be3533f"  # Your UTXO
    vout = 0

    seq = Sequence(TYPE_RELATIVE_TIMELOCK, relative_blocks)
    seq_for_n_seq = seq.for_input_sequence()

    txin = TxInput(txid, vout, sequence=seq_for_n_seq)
    p2pkh_sk = PrivateKey(conf.get("testnet3", "private_key_wif"))
    p2pkh_pk = p2pkh_sk.get_public_key().to_hex()
    p2pkh_addr = p2pkh_sk.get_public_key().get_address()

    # Build redeem script
    redeem_script = Script([
        seq.for_script(),
        "OP_CHECKSEQUENCEVERIFY",
        "OP_DROP",
        "OP_DUP",
        "OP_HASH160",
        p2pkh_addr.to_hash160(),
        "OP_EQUALVERIFY",
        "OP_CHECKSIG",
    ])

    # Output to any P2PKH address
    to_addr = P2pkhAddress("mn3XG8tZQjyUsoAmECTYFqVUECNJzEdapj")
    txout = TxOutput(to_satoshis(0.00000588), to_addr.to_script_pub_key())

    tx = Transaction([txin], [txout])
    print("Raw unsigned transaction:", tx.serialize())

    sig = p2pkh_sk.sign_input(tx, 0, redeem_script)
    txin.script_sig = Script([sig, p2pkh_pk, redeem_script.to_hex()])
    signed_tx = tx.serialize()
    print("Raw signed transaction:", signed_tx)
    print("TxId:", tx.get_txid())

    # Broadcast transaction
    mempool_api = "https://mempool.space/testnet/api/tx"
    try:
        response = requests.post(mempool_api, data=signed_tx)
        if response.status_code == 200:
            txid = response.text
            print(f"Success! TxID: {txid}")
            print(f"View transaction: https://mempool.space/testnet/tx/{txid}")
        else:
            print(f"Broadcast failed: {response.text}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main() 