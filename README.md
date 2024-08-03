# Tmux Script Automation

This script automates the execution of multiple scripts using `tmux` and `expect`. It handles password input automatically and logs the execution output.

## Prerequisites

- `tmux` must be installed on your system.
- `expect` must be installed on your system.
- Python 3.x

## Setup

1. Clone the repository or download the script.
2. Ensure the scripts you want to run are in the same directory as this script.
3. Modify the `script_table` in the `main` function to include your scripts and their respective delays.

## Usage

1. Open a terminal.
2. Navigate to the directory containing the script.
3. Run the script:

    ```bash
    python tmux_script_automation.py
    ```

## Configuration

- **Password**: The password for `sudo` commands is set in the `PASSWORD` variable. Change it to match your password.
- **Session Name**: The `SESSION_NAME` variable defines the tmux session name. Modify it if needed.

## How It Works

1. The script initializes a new `tmux` session.
2. For each script in the `script_table`:
   - A new `tmux` window is created.
   - An `expect` script is generated to handle password input and logging.
   - The script is executed with the specified delay.
3. After all scripts are set up, the script attaches to the `tmux` session so you can monitor the execution.

## Logs

Logs are saved in the `logs` directory with a timestamped filename for each script.

## Example

```python
# List of scripts and their respective delays in seconds
script_table = [
    ("test1.sh", 0),    # (script_name, delay)
    ("test2.sh", 5),
    ("test3.sh", 10),
    # Add new scripts and delays here by adding new tuples
]
