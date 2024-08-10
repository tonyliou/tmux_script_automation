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

def run_script(script_name, password, delay, session_name, user_type):
    # Generate window name, use the script filename (without extension) as the window name
    window_name = os.path.splitext(script_name)[0]

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Generate log file path
    log_file = f"logs/{window_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

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

    # List of scripts, delays, and user types
    script_table = [
        ("test1.sh", 0, 'sudo'),    # (script_name, delay, user_type)
        ("test2.sh", 5, 'user'),
        ("test3.sh", 10, 'user'),
        # Add new scripts, delays, and user types here by adding new tuples
    ]

    # Create a tmux window for each script and run it with the specified delay
    for script, delay, user_type in script_table:
        run_script(script, password, delay, session_name, user_type)

    # Attach to the session to view
    subprocess.run(["tmux", "attach", "-t", session_name])

if __name__ == "__main__":
    main()
