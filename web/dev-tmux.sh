#!/bin/bash

# Start a new tmux session named 'dev' or attach if it exists
tmux new-session -d -s dev 2>/dev/null || tmux attach-session -t dev

# Create the layout
# Split window vertically (left: claude, right: other panes)
tmux split-window -h -p 50

# Now we have two panes: 0 (left) and 1 (right)
# Select the right pane and split it horizontally twice to create 3 panes
tmux select-pane -t 1
tmux split-window -v -p 66  # Creates pane 2 (middle right)
tmux split-window -v -p 50  # Creates pane 3 (bottom right)

# Run commands in each pane
# Left pane (0): npx claude
tmux select-pane -t 0
tmux send-keys "npx claude" C-m

# Upper right pane (1): bun dev server
tmux select-pane -t 1
tmux send-keys "bun --bun run dev" C-m

# Middle right pane (2): Empty for now
tmux select-pane -t 2

# Bottom right pane (3): Empty for now
tmux select-pane -t 3

# Select the left pane (claude) as the active pane
tmux select-pane -t 0

# Attach to the session
tmux attach-session -t dev