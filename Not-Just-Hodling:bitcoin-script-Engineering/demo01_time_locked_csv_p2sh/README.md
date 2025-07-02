# bitcoin-script-engineering-demo

This project accompanies the article "Not Just HODLing: Real Bitcoin Script Engineering in 2025" and demonstrates how to use Python to construct and spend a P2SH script with a CSV timelock, broadcasting it on the Bitcoin testnet.

## Files

- `01_create_p2sh_csv_p2pkh_address.py`: Generate a P2SH address with a CSV timelock
- `02_spend_p2sh_csv_p2pkh.py`: Spend from the P2SH address
- `wa_info.conf.example`: Configuration file template. Copy to `wa_info.conf` and fill in your private key

## Usage

1. Install dependencies: `pip install bitcoinutils`
2. Copy `wa_info.conf.example` to `wa_info.conf` and fill in your private key
3. Run `01_create_p2sh_csv_p2pkh_address.py` to generate the address
4. Send testnet coins to the generated P2SH address
5. After the required number of blocks, run `02_spend_p2sh_csv_p2pkh.py` to spend from the address

## Reference Article

- [Not Just HODLing: Real Bitcoin Script Engineering in 2025](https://mempool.space/testnet/tx/34f5bf0cf328d77059b5674e71442ded8cdcfc723d0136733e0dbf180861906f) 