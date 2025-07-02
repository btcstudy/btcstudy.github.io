# Construct a Taproot address with four leaf scripts

from bitcoinutils.setup import setup
from bitcoinutils.keys import PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.transactions import Sequence
from bitcoinutils.utils import to_satoshis

import hashlib
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK

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

    # Bob's private key, for multisig and CSV timelock script path
    bob_priv = PrivateKey(conf.get("default", "bob_private_key_wif"))
    bob_pub = bob_priv.get_public_key()    
    print(f"Bob's pubkey: {bob_pub.to_hex()}, len: {len(bob_pub.to_hex())}")

    # Script 1: Verify SHA256(preimage) == hash(helloworld)
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
    relative_blocks = 2 # 2 blocks on testnet3, needs about 20 minutes to unlock
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

    # Generate Taproot address
    address = alice_pub.get_taproot_address(tree)
    print("🪙 Please send funds to this Taproot address:", address.to_string())
    conf.set('default', 'tr_4leaf_scripts_addr', address.to_string())
    conf.write(open(conf_file, "w"))

if __name__ == '__main__':
    main()