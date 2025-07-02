from bitcoinutils.setup import setup
from bitcoinutils.transactions import Sequence
from bitcoinutils.keys import P2shAddress, PrivateKey
from bitcoinutils.script import Script
from bitcoinutils.constants import TYPE_RELATIVE_TIMELOCK
import os, sys
import configparser

# Read config file and get private key
conf = configparser.ConfigParser()
conf_file = os.path.join(os.path.abspath(os.path.dirname(sys.argv[0])), "wa_info.conf")
conf.read(conf_file)

def main():
    setup("testnet")
    relative_blocks = 3  # Timelock block count

    seq = Sequence(TYPE_RELATIVE_TIMELOCK, relative_blocks)
    p2pkh_sk = PrivateKey(conf.get("testnet3", "private_key_wif"))
    p2pkh_addr = p2pkh_sk.get_public_key().get_address()

    # Build P2PKH redeem script with CSV timelock
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
    print(f"Redeem script (hex): {redeem_script.to_hex()}")

    # Generate P2SH address
    addr = P2shAddress.from_script(redeem_script)
    print(f"P2SH address: {addr.to_string()}")

    # Save to config file
    conf.set('testnet3', 'p2sh_csv_addr', addr.to_string())
    with open(conf_file, "w") as f:
        conf.write(f)

if __name__ == "__main__":
    main() 