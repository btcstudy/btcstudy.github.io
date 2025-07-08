# Taproot 4-Leaf Merkle Tree: Full Testnet Implementation & Control Block Analysis

This project demonstrates the **first complete implementation of a 4-leaf Taproot script tree**, featuring full testnet transactions, byte-level control block parsing, and witness stack execution analysis.

📖 Accompanying article:  
👉 [Medium: Building a 4-Leaf Taproot Tree in Python](https://medium.com/@aaron.recompile/building-a-4-leaf-taproot-tree-in-python-the-first-complete-implementation-on-bitcoin-testnet-c8b66c331f29)

## 🔍 Overview

We construct a Taproot address with **4 script leaves**, each representing a different spending condition:

1. `OP_SHA256` + `OP_EQUAL` hashlock
2. 2-of-2 multisig (`Alice & Bob`)  
3. CSV + `OP_CHECKSIG` for Bob
4. `OP_CHECKSIG` for bob  

Key features:

- ✅ Merkle tree generation and Taproot address construction  
- ✅ Control block creation for each script path  
- ✅ Testnet spending transactions and validation  
- ✅ Byte-by-byte control block analysis  
- ✅ Witness stack decoding and script execution visualization

## 📸 Sample Visuals

**Merkle Tree Layout:**
           Root Hash
               /         \
         Branch0         Branch1
        /      \        /       \
  Script0   Script1  Script2  Script3
  (Hash)    (Multi)   (CSV)    (Sig)

  **Stack Execution Example (Script Path Spend):**

![stack-diagram](../stack_execution_diagram.png)

## 🔗 Related Articles

- [Part 1: Build a 4-leaf Taproot Tree in Python](https://medium.com/@aaron.recompile/building-a-4-leaf-taproot-tree-in-python-the-first-complete-implementation-on-bitcoin-testnet-c8b66c331f29)
- [Part 2: Deep Dive into Taproot Control Blocks](https://medium.com/@aaron.recompile/taproot-control-block-deep-analysis-stack-execution-visualization-5ff10f98032c)

Coming soon:
- Part 3: Interactive Taproot Script Simulator (WIP)

## 🧠 Learn More

This project is part of the series:

**🛠️ Not Just HODLing: Real Bitcoin Script Engineering**  
A hands-on collection of Taproot use cases for developers, learners, and researchers.

## 🙋‍♂️ Author

Aaron Zhang([@aaron.recompile](https://medium.com/@aaron.recompile))  
[GitHub: btcstudy](https://github.com/btcstudy)

Feel free to fork, experiment, and share feedback or issues.
