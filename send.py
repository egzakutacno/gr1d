import csv
import os
import sys
import argparse
from web3 import Web3
from eth_account import Account

def parse_args():
    p = argparse.ArgumentParser(
        description="Batch‐send ETH on Arbitrum Sepolia with dynamic gas estimation")
    p.add_argument(
        "--rpc",
        required=False,
        default=os.getenv("RPC_URL"),
        help="Arbitrum Sepolia RPC endpoint (or set RPC_URL)")
    p.add_argument(
        "--key",
        required=False,
        default=os.getenv("PRIVATE_KEY"),
        help="Sender private key (or set PRIVATE_KEY)")
    p.add_argument(
        "--recipients",
        required=True,
        help="Path to CSV with columns: address,amount_in_eth")
    return p.parse_args()

def main():
    args = parse_args()

    # 1) RPC + Key
    if not args.rpc:
        print("Error: RPC URL not provided (--rpc or RPC_URL env)", file=sys.stderr)
        sys.exit(1)
    if not args.key:
        print("Error: Private key not provided (--key or PRIVATE_KEY env)", file=sys.stderr)
        sys.exit(1)

    w3 = Web3(Web3.HTTPProvider(args.rpc))
    if not w3.is_connected():
        print("Error: cannot connect to RPC", file=sys.stderr)
        sys.exit(1)

    acct = Account.from_key(args.key)
    print(f"Using account: {acct.address}")

    # 2) Load recipients.csv
    try:
        with open(args.recipients) as f:
            rows = list(csv.DictReader(f))
    except Exception as e:
        print(f"Error reading recipients file: {e}", file=sys.stderr)
        sys.exit(1)

    # 3) Prepare chain and nonce
    nonce = w3.eth.get_transaction_count(acct.address)
    chain_id = 421614  # Arbitrum Sepolia

    # 4) Process each recipient
    for row in rows:
        to = row["address"].strip()
        eth_amt = float(row["amount_in_eth"])
        value = w3.to_wei(eth_amt, "ether")

        # Build unsigned tx (without gas)
        unsigned_tx = {
            "chainId": chain_id,
            "nonce": nonce,
            "to": to,
            "value": value,
            "gasPrice": w3.eth.gas_price,
        }

        # Dynamically estimate gas based on this tx
        try:
            estimated = w3.eth.estimate_gas({
                "from": acct.address,
                "to": to,
                "value": value
            })
            unsigned_tx["gas"] = estimated
        except Exception as e:
            print(f"Error estimating gas for {to}: {e}", file=sys.stderr)
            # Fallback to a safe gas limit if estimation fails
            unsigned_tx["gas"] = 50000

        # Sign & send
        signed = acct.sign_transaction(unsigned_tx)
        try:
            tx_hash = w3.eth.send_raw_transaction(signed.raw_transaction)
            print(f"  → {to}: {eth_amt} ETH  tx hash: {tx_hash.hex()}")
        except Exception as e:
            print(f"Failed to send to {to}: {e}", file=sys.stderr)

        nonce += 1

    print("All transactions processed.")

if __name__ == "__main__":
    main()
