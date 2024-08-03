import os
import subprocess
import time
from datetime import datetime

# Define the password
PASSWORD = "1234"

# Create a new tmux session name
SESSION_NAME = "automation"

def initialize_tmux_session():
    subprocess.run(["tmux", "new-session", "-d", "-s", SESSION_NAME])

def create_expect_script(script_name, password, log_file):
    expect_script_content = f"""
set timeout -1
spawn sudo ./{script_name}
expect "password for *:"
send "{password}\\r"
log_file {log_file}
log_user 1
interact
"""
    script_path = f"{script_name}.exp"
    with open(script_path, 'w') as file:
        file.write(expect_script_content)
    return script_path

def run_script(script_name, delay):
    # Generate window name, use the script filename (without extension) as the window name
    window_name = os.path.splitext(script_name)[0]

    # Ensure logs directory exists
    os.makedirs("logs", exist_ok=True)

    # Generate log file path
    log_file = f"logs/{window_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log"

    # Create expect script
    expect_script = create_expect_script(script_name, PASSWORD, log_file)

    # Create a new window
    tmux_command = f"""
    tmux new-window -t {SESSION_NAME} -n {window_name} "bash -c 'sleep {delay}; expect {expect_script} 2>&1 | tee {log_file}; echo \\"Script {script_name} finished. Press Enter to return to bash.\\"; read; exec bash'"
    """
    subprocess.run(tmux_command, shell=True, executable="/bin/bash")

def main():
    initialize_tmux_session()

    # List of scripts and their respective delays in seconds
    script_table = [
        ("test1.sh", 0),    # (script_name, delay)
        ("test2.sh", 5),
        ("test3.sh", 10),
        # Add new scripts and delays here by adding new tuples
    ]

    # Create a tmux window for each script and run it with the specified delay
    for script, delay in script_table:
        run_script(script, delay)

    # Attach to the session to view
    subprocess.run(["tmux", "attach", "-t", SESSION_NAME])

if __name__ == "__main__":
    main()
