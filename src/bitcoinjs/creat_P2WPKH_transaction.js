/**
 * This script is used to create and send a Bitcoin transaction on the testnet.
 * It uses the bitcoinjs-lib library for transaction creation and signing, and axios for HTTP requests.
 * 
 * The script does the following:
 * 1. Fetches the UTXOs for a given source address.
 * 2. Creates a new transaction using these UTXOs, sending a specified amount to a destination address.
 * 3. Calculates the transaction fee based on the size of the transaction (110 satoshis per byte).
 * 4. If there's any change left over after subtracting the amount to send and the fee, it adds a change output back to the source address.
 * 5. Signs the transaction inputs with a given private key.
 * 6. Finalizes the transaction and gets it in hex format.
 * 7. Broadcasts the transaction to the Bitcoin testnet using the Blockstream API.
 * 
 * To use this script, you need to replace the `privateKey`, `sourceAddress`, and `destinationAddress` variables with your own values.
 * You also need to set the `amountToSend` variable to the amount you want to send (in satoshis).
 * 
 * Note: This script assumes that all UTXOs for the source address are P2WPKH UTXOs.
 * If the UTXOs are of a different type, the script may not work correctly.
 * 
 * Also note that the transaction size estimation is a rough approximation. The actual transaction size may be slightly different.
 * The fee rate of 110 satoshis per byte is just an example. The optimal fee rate can vary depending on the current network conditions.
 */
const bitcoin = require('bitcoinjs-lib');
const axios = require('axios');

async function sendTransaction() {
    const testnet = bitcoin.networks.testnet;

    // Replace these with your own values
    const privateKey = 'cPp3aDLJiHADoFnQkPRtaNmV4u9u5GyuKuK6MpGVeVP3CcoDUEVM';
    const sourceAddress = 'tb1q23c3l56jr86zr2jxkrpv7whjs0kt6qcghrgrfp';
    const destinationAddress = 'tb1qlnfnlzjn28g7v37aseqhlrr3jytvmdk9jtwm6m';
    const amountToSend = 1000; // in satoshis

    const keyPair = bitcoin.ECPair.fromWIF(privateKey, testnet);

    const psbt = new bitcoin.Psbt({ network: testnet });

    // Fetch the UTXOs for the source address
    const { data: utxos } = await axios.get(`https://blockstream.info/testnet/api/address/${sourceAddress}/utxo`);

    if (utxos.length === 0) {
        throw new Error('No UTXOs found for this address');
    }

    let totalUtxos = 0;
    for (let utxo of utxos) {
        // Fetch the transaction data for the UTXO
        const { data: txData } = await axios.get(`https://blockstream.info/testnet/api/tx/${utxo.txid}`);

        // Extract the scriptpubkey from the transaction output
        const scriptpubkey = txData.vout[utxo.vout].scriptpubkey;
        console.log('scriptpubkey:', scriptpubkey);

        psbt.addInput({
            hash: utxo.txid,
            index: utxo.vout,
            witnessUtxo: {
                script: Buffer.from(scriptpubkey, 'hex'),
                value: utxo.value,
            },
        });
        totalUtxos += utxo.value;
        if (totalUtxos >= amountToSend) break;
    }
    console.log('totalUtxos:', totalUtxos);
    console.log('inputs:', psbt.data.inputs);

    psbt.addOutput({
        address: destinationAddress,
        value: amountToSend,
    });

    console.log('outputs:', psbt.data.outputs);

    // Calculate the transaction fee (1 satoshi per byte is a reasonable fee)
    const transactionSize = psbt.data.inputs.length * 180 + psbt.data.outputs.length * 34 + 10 + psbt.data.inputs.length;
    const fee = transactionSize * 10;
    console.log('fee:', fee);
    
    // Calculate the change and add it as an output
    const change = totalUtxos - amountToSend - fee;

    console.log('change:', change);

    if (change > 0) {
        psbt.addOutput({
            address: sourceAddress,
            value: change,
        });
    }

    // Sign the inputs
    psbt.signAllInputs(keyPair);

    // Finalize the transaction
    psbt.finalizeAllInputs();

    // Get the transaction in hex format
    const txHex = psbt.extractTransaction().toHex();

    // Broadcast the transaction
    const { data: txid } = await axios.post('https://blockstream.info/testnet/api/tx', txHex);

    console.log('Transaction ID:', txid);
}

sendTransaction().catch(console.error);