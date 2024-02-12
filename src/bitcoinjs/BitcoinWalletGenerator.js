/*
File: BitcoinWalletGenerator.js

Description:
This script provides functionalities for generating a Bitcoin wallet using BitcoinJS, BIP39, and BIP32 standards.
It includes the generation of a mnemonic phrase for seed creation, deriving key pairs from the mnemonic,
and creating wallet addresses for both primary and funding purposes on the Bitcoin testnet.

Features:
- Generate a mnemonic phrase for wallet seed.
- Create key pairs based on the provided mnemonic phrase and derivation paths.
- Generate wallet addresses for primary and funding transactions on the Bitcoin testnet.

Usage:
Simply run this script in a Node.js environment. The script will generate a new Bitcoin wallet,
print the wallet's mnemonic phrase, primary address, funding address, and their respective WIFs.

Dependencies:
- bitcoinjs-lib: A library for Bitcoin protocol.
- bip39: For mnemonic phrase generation and seed creation.
- bip32: For hierarchical deterministic wallet functions.

Note:
This script is configured for the Bitcoin testnet. Modify the `network` parameter in the `createKeyPair` function calls
for use with other networks.
*/

const bitcoin = require('bitcoinjs-lib');
const bip39 = require('bip39');
const bip32 = require('bip32');

function createMnemonicPhrase() {
    const mnemonic = bip39.generateMnemonic();
    return {
        phrase: mnemonic
    }
}

async function createKeyPair(phrase, path, network) {
    const seed = await bip39.mnemonicToSeed(phrase);
    const rootKey = bip32.fromSeed(seed, network);
    const childKey = rootKey.derivePath(path);

    const { address } = bitcoin.payments.p2wpkh({ pubkey: childKey.publicKey, network });

    return {
        address: address,
        path,
        WIF: childKey.toWIF(),
    }
}

async function createWallet() {
    const phraseResult = createMnemonicPhrase();
    const phrase = phraseResult.phrase;

    const primary = await createKeyPair(phrase, `m/84'/1'/0'/0/0`, bitcoin.networks.testnet);
    const funding = await createKeyPair(phrase, `m/84'/1'/0'/1/0`, bitcoin.networks.testnet);

    return {
        phrase: phrase,
        primary: primary,
        funding: funding,
    }
}

createWallet()
    .then(wallet => {
        console.log('Wallet Data:', wallet);
    })
    .catch(error => {
        console.error('Error:', error);
    });