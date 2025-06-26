import subprocess
import json
import time
import os

IMAGE_NAME = "my-ubuntu-systemd-with-docker"
CIRCUIT_NODE_IMAGE = "gr1dnetwork/circuit-node"

def run_cmd(cmd):
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return proc.returncode, proc.stdout.strip(), proc.stderr.strip()

def container_exists(name):
    ret, out, _ = run_cmd(["docker", "ps", "-a", "-q", "-f", f"name=^{name}$"])
    return bool(out.strip())

def create_container(name):
    if container_exists(name):
        print(f"⚠️ Container {name} already exists, skipping creation")
        return False
    ret, out, err = run_cmd([
        "docker", "run", "--privileged", "--cgroupns=host",
        "--name", name,
        "--restart=always",
        "-v", "/sys/fs/cgroup:/sys/fs/cgroup",
        "-d", IMAGE_NAME,
        "/lib/systemd/systemd"  # ✅ This ensures systemd is PID 1
    ])
    if ret == 0:
        print(f"✅ Container {name} created")
        return True
    else:
        print(f"❌ Failed to create {name}: {err}")
        return False

def wait_for_inner_docker(container_name, timeout=30):
    for _ in range(timeout):
        ret, out, _ = run_cmd([
            "docker", "exec", container_name,
            "docker", "info"
        ])
        if ret == 0:
            return True
        time.sleep(1)
    return False

def run_circuit_node(container_name):
    if not wait_for_inner_docker(container_name):
        print(f"❌ Docker not ready in {container_name}, skipping app start.")
        return

    cmd = (
        "mkdir -p ~/flohive && "
        "docker rm -f circuit-node >/dev/null 2>&1 || true && "
        f"docker run --restart=always --name circuit-node --pull always -v ~/flohive:/app/cache {CIRCUIT_NODE_IMAGE} > /dev/null 2>&1 &"
    )
    ret, _, err = run_cmd(["docker", "exec", container_name, "bash", "-c", cmd])
    if ret == 0:
        print(f"🚀 Started circuit-node in {container_name}")
    else:
        print(f"⚠️ Failed to start circuit-node in {container_name}: {err}")

def get_keys(container_name, retries=12, delay=5):
    for attempt in range(retries):
        ret, stdout, _ = run_cmd([
            "docker", "exec", container_name,
            "cat", "/root/flohive/flohive-cache.json"
        ])
        if ret == 0:
            try:
                data = json.loads(stdout)
                pk = data.get("burnerWallet", {}).get("privateKey")
                addr = data.get("burnerWallet", {}).get("address")
                return pk, addr
            except json.JSONDecodeError:
                pass
        time.sleep(delay)
    return None, None

def save_keys_to_file(prefix, count, results):
    os.makedirs("/root/wallets", exist_ok=True)
    filename = f"/root/wallets/{prefix}_1-{prefix}_{count}.txt"
    with open(filename, "w") as f:
        for i in range(1, count + 1):
            pk, addr = results.get(i, (None, None))
            f.write(f"{prefix}_{i}:\n")
            if pk and addr:
                f.write(f"  privateKey: {pk}\n")
                f.write(f"  address:    {addr}\n")
            else:
                f.write("  ⚠️ Could not find keys or file missing\n")
            f.write("-" * 30 + "\n")
    print(f"\n💾 Saved keys to file: {filename}")

def main():
    prefix = input("Enter container name prefix (e.g. grid): ").strip()
    if not prefix:
        print("Prefix cannot be empty.")
        return

    try:
        count = int(input("How many containers do you want to create? "))
        if count < 1:
            print("Please enter a positive integer.")
            return
    except ValueError:
        print("Invalid input. Please enter a number.")
        return

    for i in range(1, count + 1):
        name = f"{prefix}_{i}"
        created = create_container(name)
        if created:
            print(f"⏳ Waiting 5 seconds for {name} to be ready...")
            time.sleep(5)
        run_circuit_node(name)

    print("\n⏳ Waiting for JSON files to be created and collected...\n")

    results = {}
    for i in range(1, count + 1):
        name = f"{prefix}_{i}"
        pk, addr = get_keys(name)
        print(f"➡️ {name}:")
        if pk and addr:
            print(f"  privateKey: {pk}")
            print(f"  address:    {addr}")
        else:
            print("  ⚠️ Could not find keys or file missing")
        print("-" * 30)
        results[i] = (pk, addr)

    save_keys_to_file(prefix, count, results)

if __name__ == "__main__":
    main()
