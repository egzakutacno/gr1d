#!/bin/bash

read -p "How many containers to create? " COUNT
read -p "Enter base name (e.g. flohive or gridd): " BASENAME

WALLET_DIR="/root/wallets"
mkdir -p "$WALLET_DIR"
WALLET_FILE="${WALLET_DIR}/${BASENAME}_1-${COUNT}.txt"

echo "Generating $COUNT containers with base name '$BASENAME'"
echo "" > "$WALLET_FILE"

for i in $(seq 1 "$COUNT"); do
  FOLDER=~/${BASENAME}_$i
  CONTAINER_NAME="${BASENAME}_$i"

  mkdir -p "$FOLDER"
  echo "[*] Starting container $CONTAINER_NAME with volume $FOLDER"
  docker run --pull always -d --restart unless-stopped --name "$CONTAINER_NAME" -v "$FOLDER":/app/cache -e OWNERS_ALLOWLIST=0x gr1dnetwork/circuit-node



  # Wait for the cache file to be created
  echo "    ⏳ Waiting for flohive-cache.json to appear..."
  for attempt in {1..20}; do
    if [[ -f "$FOLDER/flohive-cache.json" ]]; then
      break
    fi
    sleep 1
  done

  if [[ -f "$FOLDER/flohive-cache.json" ]]; then
    address=$(jq -r '.burnerWallet.address' "$FOLDER/flohive-cache.json")
    privkey=$(jq -r '.burnerWallet.privateKey' "$FOLDER/flohive-cache.json")

    echo "    ✅ $CONTAINER_NAME wallet"
    echo "    Address: $address"
    echo "    PrivKey: $privkey"

    echo "$CONTAINER_NAME:" >> "$WALLET_FILE"
    echo "  Address: $address" >> "$WALLET_FILE"
    echo "  PrivateKey: $privkey" >> "$WALLET_FILE"
    echo "" >> "$WALLET_FILE"
  else
    echo "    ❌ Failed to find flohive-cache.json for $CONTAINER_NAME"
  fi
done

echo -e "\nAll wallets saved to: $WALLET_FILE"
