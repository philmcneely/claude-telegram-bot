#!/bin/bash
# Start Claude Code in a tmux session.
# The bot talks to Claude through this tmux session.

SESSION_NAME="${TMUX_SESSION:-claude}"

# Check if tmux is installed
if ! command -v tmux &> /dev/null; then
    echo "Error: tmux is not installed."
    echo ""
    echo "Install it:"
    echo "  Mac:    brew install tmux"
    echo "  Ubuntu: sudo apt install tmux"
    echo "  Fedora: sudo dnf install tmux"
    exit 1
fi

# Check if Claude Code is installed
if ! command -v claude &> /dev/null; then
    echo "Error: Claude Code is not installed."
    echo ""
    echo "Install it:"
    echo "  npm install -g @anthropic-ai/claude-code"
    echo ""
    echo "You also need a Claude subscription (Pro $20/mo or Max $100-200/mo)"
    echo "OR point it at a local model (see README for instructions)."
    exit 1
fi

# Kill existing session if any
tmux kill-session -t "$SESSION_NAME" 2>/dev/null

# Create new tmux session with a wide terminal
tmux new-session -d -s "$SESSION_NAME" -x 200 -y 50

# Launch Claude Code inside it
# --dangerously-skip-permissions: no confirmation prompts
# Remove this flag if you want Claude to ask before each action
tmux send-keys -t "$SESSION_NAME" 'claude --dangerously-skip-permissions' Enter

echo "Claude Code is running in tmux session '$SESSION_NAME'."
echo ""
echo "To see it:     tmux attach -t $SESSION_NAME"
echo "To detach:     Ctrl+B then D"
echo "To stop it:    tmux kill-session -t $SESSION_NAME"
echo ""
echo "Now start the bot:  python3 bot.py"
