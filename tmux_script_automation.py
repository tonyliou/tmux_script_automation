import os
import subprocess
import time
from datetime import datetime
import argparse

def initialize_tmux_session(session_name):
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name])

def create_expect_script(script_name, password, log_file, user_type):
    if user_type == 'sudo':
        expect_script_content = f"""
set timeout -1
spawn sudo ./{script_name}
expect "password for *:"
send "{password}\\r"
log_file {log_file}
log_user 1
interact
"""
    else:
        expect_script_content = f"""
set timeout -1
spawn ./{script_name}
log_file {log_file}
log_user 1
interact
"""

    script_path = f"{script_name}.exp"
    with open(script_path, 'w') as file:
        file.write(expect_script_content)
    return script_path

def run_script(script_name, user_type, delay, password, session_name, logs_dir):
    # Generate window name, use the script filename (without extension) as the window name
    window_name = os.path.splitext(script_name)[0]

    # Generate log file path inside the timestamped logs directory
    log_file = f"{logs_dir}/{window_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

    # Create expect script
    expect_script = create_expect_script(script_name, password, log_file, user_type)

    # Create a new window
    tmux_command = f"""
    tmux new-window -t {session_name} -n {window_name} "bash -c 'sleep {delay}; expect {expect_script} 2>&1 | tee {log_file}; echo \\"Script {script_name} finished. Press Enter to return to bash.\\"; read; exec bash'"
    """
    subprocess.run(tmux_command, shell=True, executable="/bin/bash")

def main():
    parser = argparse.ArgumentParser(description='Automate tmux sessions with expect scripts.')
    parser.add_argument('--password', required=True, help='Password for sudo')
    args = parser.parse_args()

    password = args.password
    session_name = "automation"
    initialize_tmux_session(session_name)

    # Create timestamped logs directory
    logs_dir = f"logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(logs_dir, exist_ok=True)

    # List of scripts, user types, and delays
    script_table = [
        ("test1.sh", 'sudo', 0),    # (script_name, user_type, delay)
        ("test2.sh", 'user', 5),
        ("test3.sh", 'sudo', 10),
        # Add new scripts, user types, and delays here by adding new tuples
    ]

    # Create a tmux window for each script and run it with the specified delay
    for script, user_type, delay in script_table:
        run_script(script, user_type, delay, password, session_name, logs_dir)

    # Attach to the session to view
    subprocess.run(["tmux", "attach", "-t", session_name])

if __name__ == "__main__":
    main()
