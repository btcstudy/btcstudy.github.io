/*
DONE! DO NOT DELET!

This script demonstrates the creation of Bitcoin addresses using the bitcore-lib library. 
It is inspired by a tutorial available at https://www.youtube.com/watch?v=ObRnmvIdecI and utilizes code from https://github.com/ezesundayeze/sendbitcoin/blob/master/src/wallet.bitcoin.js.

*/



const { PrivateKey } = require("bitcore-lib");

const { mainnet, testnet } = require("bitcore-lib/lib/networks");

const Mnemonic = require("bitcore-mnemonic");

const createWallet = (network = testnet) => {

  var privateKey = new PrivateKey();
  var address = privateKey.toAddress(network);
  return {
    privateKey: privateKey.toString(),
    address: address.toString(),
  };
};

// Call the createWallet function to generate a new wallet
const wallet = createWallet();

// Now log the privateKey and address from the wallet object
console.log('privateKey:',wallet.privateKey);
console.log('address:',wallet.address);

/**
A Hierarchical Deterministic (HD) wallet is the term used to describe a wallet which uses a seed to derive public and private keys
**/

const createHDWallet = (network = mainnet) => {
  let passPhrase = new Mnemonic(Mnemonic.Words.SPANISH);
  let xpriv = passPhrase.toHDPrivateKey(passPhrase.toString(), network);

  return {
    xpub: xpriv.xpubkey,
    privateKey: xpriv.privateKey.toString(),
    address: xpriv.publicKey.toAddress().toString(),
    mnemonic: passPhrase.toString(),
  };
};

module.exports = {
  createHDWallet,
  createWallet,
};

// Call the createWallet function to generate a new wallet
const wallet2 = createHDWallet();

// Now log the privateKey and address from the wallet object
console.log('xpub:',wallet2.xpub);
console.log('privatekey:',wallet2.privateKey);
console.log('address:',wallet2.address);
console.log('mnemonic:',wallet2.mnemonic);