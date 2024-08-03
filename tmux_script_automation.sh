#!/bin/bash

# Define the password
PASSWORD="1234"

# Create a new tmux session name
SESSION_NAME="automation"

# Initialize the tmux session
initialize_tmux_session() {
    tmux new-session -d -s $SESSION_NAME
}

# Run a single script with delay
run_script() {
    local script_name=$1
    local delay=$2

    # Generate window name, use the script filename (without extension) as the window name
    local window_name="${script_name%.*}"

    # Ensure logs directory exists
    mkdir -p "logs"

    # Generate log file path
    local log_file="logs/${window_name}_$(date '+%Y-%m-%d_%H-%M-%S').log"

    # Create a new window
    tmux new-window -t $SESSION_NAME -n $window_name "bash -c 'sleep $delay; expect -c \"
        set timeout -1
        spawn sudo ./$script_name
        expect \\\"password for *:\\\"
        send \\\"$PASSWORD\r\\\"
        log_file $log_file
        log_user 1
        interact
    \" 2>&1 | tee $log_file; echo \"Script $script_name finished. Press Enter to return to bash.\"; read; exec bash'"
}

# Main function
main() {
    initialize_tmux_session

    # List of scripts and their respective delays in seconds
    declare -a scripts=(
        "test1.sh"
        "test2.sh"
        "test3.sh"
        # Add new scripts here by adding new lines
    )

    declare -a delays=(
        0    # Delay for test1.sh
        5    # Delay for test2.sh
        10   # Delay for test3.sh
        # Add new delays here corresponding to the scripts
    )

    # Create a tmux window for each script and run it with the specified delay
    for i in "${!scripts[@]}"; do
        run_script "${scripts[$i]}" "${delays[$i]}"
    done

    # Attach to the session to view
    tmux attach -t $SESSION_NAME
}

# Execute main function
main
