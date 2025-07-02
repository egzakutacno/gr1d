import subprocess

def run_cmd(cmd):
    result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result.returncode, result.stdout.strip(), result.stderr.strip()

def check_log(container_name):
    # Just check one line to test connectivity
    cmd = [
        "docker", "exec", container_name,
        "docker", "logs", "--tail", "1", "circuit-node"
    ]
    ret, out, err = run_cmd(cmd)

    if ret != 0 or "Error" in out or "Error" in err or "No such container" in err:
        print(f"❌ {container_name} has a problem: {err or out}")
        restart_container(container_name)
    else:
        print(f"✅ {container_name} is healthy")

def restart_container(container_name):
    print(f"🔁 Restarting {container_name}...")
    ret, out, err = run_cmd(["docker", "restart", container_name])
    if ret == 0:
        print(f"✅ {container_name} restarted")
    else:
        print(f"❌ Failed to restart {container_name}: {err}")

def main():
    prefix = input("Enter container name prefix (e.g. grid): ").strip()
    try:
        count = int(input("How many containers to check? "))
    except ValueError:
        print("Invalid number")
        return

    print(f"\n🔍 Checking logs of {prefix}_1 to {prefix}_{count}...")
    for i in range(1, count + 1):
        name = f"{prefix}_{i}"
        check_log(name)

if __name__ == "__main__":
    main()
