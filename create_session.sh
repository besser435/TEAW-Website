#!/bin/bash

SESSION_NAME="teaw"

setup_tmux_session() {
    echo "Starting TEAW tmux session..."
    
    tmux new-session -d -s "$SESSION_NAME"

    tmux rename-window -t 0 'webserver'
    tmux send-keys -t 'webserver' "cd /home/brandon/Desktop/TEAW-Website/web" C-m
    tmux send-keys -t 'webserver' "bash run_prod.sh" C-m

    tmux new-window -t "$SESSION_NAME:1" -n 'db_updater'
    tmux send-keys -t 'db_updater' "cd /home/brandon/Desktop/TEAW-Website/db_updater" C-m
    tmux send-keys -t 'db_updater' "python db_updater.py" C-m

    tmux new-window -t "$SESSION_NAME:2" -n 'stats_updater'
    tmux send-keys -t 'stats_updater' "cd /home/brandon/Desktop/TEAW-Website/db_updater" C-m
    tmux send-keys -t 'stats_updater' "python stats_updater.py" C-m
}

main() {
    setup_tmux_session

    tmux attach-session -t "$SESSION_NAME"
    echo "--- NOTE: Ensure Processes Started Successfully ---"
}

main