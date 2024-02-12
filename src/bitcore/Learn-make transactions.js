/*

DONE! DO NOT DELETE!
This script demonstrates the manual creation of a Bitcoin transaction using the bitcore-lib library. It follows the tutorial available at https://www.youtube.com/watch?v=ObRnmvIdecI and uses source code from https://github.com/ezesundayeze/sendbitcoin/blob/master/src/send.bitcoin.js.

Please note that this script is intended for use on the Bitcoin testnet and has been verified to work correctly.

Important Note: Ensure that a traditional Pay-to-Public-Key-Hash (P2PKH) address is used for transactions. While transactions can be built and serialized using SegWit addresses, attempting to broadcast such transactions will result in the error "non-mandatory-script-verify-flag (Witness requires empty scriptSig)."

*/

const axios = require("axios");
const bitcore = require("bitcore-lib");

const sendBitcoin = async (receiverAddress, amountToSend) => {
  console.log("hello inside sendBitcoin");
  const TESTNET = true;
  try {
    const network = bitcore.Networks.testnet;

    const privateKey = "cNS9RbsxDBA8ES8ZEFQ5rQNfaC1hGsaUdPc8LUKwwhjjWbu4a1oA";
  
    const sourceAddress = "n1YPFMwBNCL6zKjEWh55mSMtAQSMDRR9RE";

    const satoshiToSend = Math.floor(amountToSend * 100000000);
    if (satoshiToSend <= 0) {
      throw new Error("Amount must be a positive value");
    }
    const recieverAddress = "n1YPFMwBNCL6zKjEWh55mSMtAQSMDRR9RE";
    
    // Initialize other required variables
    let fee = 0;
    let inputCount = 0;
    let outputCount = 2; // Assuming there's one output plus change
    let totalAmountAvailable = 0;
    let inputs = [];

    // Fetch UTXOs for the sourceAddress
    const utxosResponse = await axios.get(`https://blockstream.info/testnet/api/address/${sourceAddress}/utxo`);
    console.log("UTXOs response:", utxosResponse.data);
    
    const utxos = utxosResponse.data;

    for (const utxo of utxos) {
      let input = {
        satoshis: utxo.value,
        script: bitcore.Script.buildPublicKeyHashOut(sourceAddress).toHex(),
        address: sourceAddress,
        txId: utxo.txid,
        outputIndex: utxo.vout
      };
      totalAmountAvailable += utxo.value;
      inputCount += 1;
      inputs.push(input);
      console.log("input", input);
    }

    // Additional transaction creation and sending logic goes here...

    /**
     * In a bitcoin transaction, the inputs contribute 180 bytes each to the transaction,
     * while the output contributes 34 bytes each to the transaction. Then there is an extra 10 bytes you add or subtract
     * from the transaction as well.
     * */
    console.log(`Source Address: ${sourceAddress}`);
    // console.log(`Derived Address from PrivateKey: ${privateKeyObj.toAddress().toString()}`);
    console.log(`privatekey Address: ${privateKey}`);
    let transaction = new bitcore.Transaction(); 

    const transactionSize =
      inputCount * 180 + outputCount * 34 + 10 - inputCount;

    fee = transactionSize * 1 / 3; // satoshi per byte
    if (TESTNET) {
      fee = transactionSize * 1 // 1 sat/byte is fine for testnet
    }
    if (totalAmountAvailable - satoshiToSend - fee < 0) {
      throw new Error("Balance is too low for this transaction");
    }
    //Set transaction input
    transaction.from(inputs);

    // set the recieving address and the amount to send
    transaction.to(recieverAddress, satoshiToSend);

    // Set change address - Address to receive the left over funds after transfer
    transaction.change(sourceAddress);

    //manually set transaction fees: 20 satoshis per byte
    transaction.fee(Math.round(fee));
    console.log("transction fee ",transaction.fee(Math.round(fee)))


    // Sign transaction with your private key
    transaction.sign(privateKey);

    // serialize Transactions
    const serializedTransaction = transaction.serialize(true);

    console.log("serializedTransaction",serializedTransaction)
     
    const result = await axios({
      method: "POST",
      url: `https://blockstream.info/testnet/api/tx`,
      data: serializedTransaction,
    });
    return result.data;



  } catch (error) {
    console.error("Error in sendBitcoin:", error);
    // Handle the error appropriately
  }
};

sendBitcoin("tb1qd56deqk2qn6fmrrsmjwtc8w5kdyyhsrp57ym6d", 0.00001);

