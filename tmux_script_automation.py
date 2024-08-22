import os
import subprocess
import time
from datetime import datetime
import argparse

def initialize_tmux_session(session_name):
    """Initialize a new tmux session."""
    subprocess.run(["tmux", "new-session", "-d", "-s", session_name])

def create_expect_script(script_name, password, log_file_path, user_type, log_enabled):
    """Create an expect script for running a shell script with or without sudo."""
    log_file_command = f"log_file {log_file_path}" if log_enabled else ""
    log_user_command = "log_user 1" if log_enabled else "log_user 0"

    if user_type == 'sudo':
        expect_script_content = (
            "set timeout -1\n"
            f"spawn sudo ./{script_name}\n"
            "expect \"password for *:\"\n"
            f"send \"{password}\\r\"\n"
            f"{log_file_command}\n"
            f"{log_user_command}\n"
            "interact\n"
        )
    else:
        expect_script_content = (
            "set timeout -1\n"
            f"spawn ./{script_name}\n"
            f"{log_file_command}\n"
            f"{log_user_command}\n"
            "interact\n"
        )

    script_path = f"{script_name}.exp"
    with open(script_path, 'w') as file:
        file.write(expect_script_content)
    return script_path

def run_script_in_tmux(script_name, user_type, delay, password, session_name, logs_dir, log_enabled):
    """Run a script in a new tmux window with optional logging."""
    window_name = os.path.splitext(script_name)[0]
    log_file_path = os.path.join(logs_dir, f"{window_name}_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.log") if log_enabled else "/dev/null"

    expect_script = create_expect_script(script_name, password, log_file_path, user_type, log_enabled)

    tmux_command = f"""
    tmux new-window -t {session_name} -n {window_name} "bash -c 'sleep {delay}; expect {expect_script} 2>&1 | {'tee ' + log_file_path if log_enabled else 'cat'}; echo \\"Script {script_name} finished. Press Enter to return to bash.\\"; read; exec bash'"
    """
    subprocess.run(tmux_command, shell=True, executable="/bin/bash")

def setup_logging_directory():
    """Create a timestamped directory to store log files."""
    logs_dir = f"logs_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
    os.makedirs(logs_dir, exist_ok=True)
    return logs_dir

def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description='Automate tmux sessions with expect scripts.')
    parser.add_argument('--password', required=True, help='Password for sudo')
    return parser.parse_args()

def main():
    args = parse_arguments()
    password = args.password
    session_name = "automation"

    initialize_tmux_session(session_name)
    logs_dir = setup_logging_directory()

    script_table = [
        ("test1.sh", 'sudo', 0,  False),  # (script_name, user_type, delay, log_enabled)
        ("test2.sh", 'user', 5,  True),
        ("test3.sh", 'sudo', 10, True),
        # Add additional scripts here
    ]

    for script, user_type, delay, log_enabled in script_table:
        run_script_in_tmux(script, user_type, delay, password, session_name, logs_dir, log_enabled)

    subprocess.run(["tmux", "attach", "-t", session_name])

if __name__ == "__main__":
    main()
