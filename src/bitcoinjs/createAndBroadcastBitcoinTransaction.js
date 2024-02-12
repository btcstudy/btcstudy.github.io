/*
 * File: buildtransaction.js
 * Purpose: This script creates and broadcasts a Bitcoin transaction on the specified network using the bitcoinjs-lib library.
 * 
 * The createAndBroadcastTransaction function takes the following parameters:
 * - inputTxHash: The transaction hash of the input (a string)
 * - inputIndex: The index of the output in the input transaction to use (a number)
 * - recipientAddress: The address to send the bitcoins to (a string)
 * - amount: The amount of bitcoins to send (a number)
 * - privateKeyWIF: The private key of the address sending the bitcoins, in Wallet Import Format (a string)
 * - network: The network to use ('testnet' or 'mainnet')
 * 
 * The function creates a transaction, signs it with the provided private key, and broadcasts it to the network.
 * It returns a promise that resolves to the transaction ID if the broadcast is successful, or rejects with an error if the broadcast fails.
 * 
 * Note: This script uses the deprecated TransactionBuilder class from bitcoinjs-lib. In future versions of the library, this class will be removed and replaced with the Psbt class.
 * 
 * Usage:
 * Uncomment the call to createAndBroadcastTransaction at the bottom of the script and replace the placeholders with your actual data.
 * Then run the script with Node.js.
 */
const axios = require('axios');
const bitcoin = require('bitcoinjs-lib');

async function createAndBroadcastTransaction(inputTxHash, inputIndex, recipientAddress, amount, privateKeyWIF, network) {
  const txNetwork = bitcoin.networks[network];
  const transaction = new bitcoin.TransactionBuilder(txNetwork);

  // Add input to the transaction
  transaction.addInput(inputTxHash, inputIndex);

  // Add output to the transaction
  transaction.addOutput(recipientAddress, amount);

  // Create an ECPair from a WIF private key
  const privateKey = bitcoin.ECPair.fromWIF(privateKeyWIF, txNetwork);

  // Sign the transaction with the private key
  transaction.sign(0, privateKey);

  console.log('transaction before build the transanction:', transaction)

  // Build the transaction
  const builtTransaction = transaction.build();

  // Serialize the transaction
  const serializedTransaction = builtTransaction.toHex();

  console.log('transaction after serialized:', serializedTransaction)

  // Broadcast the transaction
  const result = await axios({
    method: "POST",
    url: `https://blockstream.info/${network}/api/tx`,
    data: serializedTransaction,
  });

  return result.data;
}


// createAndBroadcastTransaction('inputTxHash', 1, 'recipientAddress', 546, 'privateKeyWIF', 'testnet')
//   .then(txId => console.log(`Transaction broadcasted. ID: ${txId}`))
//   .catch(error => console.error(`Error broadcasting transaction: ${error.message}`));


  createAndBroadcastTransaction('a5776cf9fbe173fb264c14f3cb661eab6646b8f58aa07a6f2c6b89d1e73d67c7', 1, 'mpwDinPvufADQJ1ygS2WvXUR7YuZSTste8', 546, 'cQLXCsYFLEcenE9kNW2poetguxLbko6v72uB1jKS1QuuuNRDmqkS', 'testnet')
  .then(txId => console.log(`Transaction broadcasted. ID: ${txId}`))
  .catch(error => console.error(`Error broadcasting transaction: ${error.message}`));