import subprocess

def get_container_list(prefix, count):
    return [f"{prefix}_{i}" for i in range(1, count + 1)]

def create_tmux_session(session_name):
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name])

def split_tmux_pane(index):
    if index == 0:
        return
    elif index % 2 == 1:
        subprocess.run(["tmux", "split-window", "-h"])
    else:
        subprocess.run(["tmux", "split-window", "-v"])
    subprocess.run(["tmux", "select-layout", "tiled"])

def send_tmux_command(container_name):
    # Proper escaping to run docker inside the outer container
    inner_cmd = "docker logs -f $(docker ps -q --filter name=circuit-node)"
    full_cmd = f"docker exec -it {container_name} bash -c '{inner_cmd}'"
    subprocess.run(["tmux", "send-keys", full_cmd, "C-m"])

def main():
    prefix = input("Enter container prefix (e.g., wokie): ").strip()
    count = int(input("How many containers to monitor?: "))

    containers = get_container_list(prefix, count)
    session_name = "nested_log_monitor"

    create_tmux_session(session_name)

    for i, container in enumerate(containers):
        if i > 0:
            split_tmux_pane(i)
        subprocess.run(["tmux", "select-pane", "-t", str(i)])
        send_tmux_command(container)

    subprocess.run(["tmux", "select-layout", "tiled"])
    subprocess.run(["tmux", "attach-session", "-t", session_name])

if __name__ == "__main__":
    main()
