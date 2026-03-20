# Claude Telegram Bot

Text Claude Code from your phone. Send a Telegram message, Claude does the work, sends you back the result.

This is the starter code from [Anthropic just shipped what I built six months ago](https://github.com/philmcneely/claude-telegram-bot).

## What it does

1. You text your Telegram bot
2. The bot types your message into a tmux session where Claude Code is running
3. Claude Code processes the request (edits files, runs tests, whatever you asked)
4. The bot captures the output and sends it back to Telegram

That's it. ~100 lines of Python. No frameworks, no dependencies beyond `requests`.

## Prerequisites

You need:

- **A computer that stays on** -- Mac, Linux, or Windows with WSL. A Mac Mini, old laptop, or NUC works great. This will be your always-on agent.
- **Python 3.8+** -- Check: `python3 --version`
- **tmux** -- Terminal multiplexer. Check: `tmux -V`
  - Mac: `brew install tmux`
  - Ubuntu/Debian: `sudo apt install tmux`
  - Fedora: `sudo dnf install tmux`
- **Claude Code** -- Anthropic's CLI tool
  - Install: `npm install -g @anthropic-ai/claude-code`
  - Requires Node.js 18+ (`brew install node` or [nodejs.org](https://nodejs.org/))
  - Requires a Claude subscription (Pro $20/mo or Max $100-200/mo) **OR** a local model (see below)
- **A Telegram bot token** -- Takes 30 seconds, free, instructions below

## Quick start

### 1. Create a Telegram bot

1. Open Telegram, search for **@BotFather**
2. Send `/newbot`
3. Pick a name (e.g., "My Claude Bot") and username (e.g., "my_claude_code_bot")
4. Copy the token it gives you (looks like `123456789:ABCdefGHI...`)

### 2. Get your chat ID

1. Open Telegram, search for **@userinfobot**
2. Send `/start`
3. It replies with your user ID (a number like `123456789`)

This is your chat ID. The bot will only respond to messages from this ID -- everyone else gets ignored.

### 3. Clone and configure

```bash
git clone https://github.com/philmcneely/claude-telegram-bot.git
cd claude-telegram-bot
pip3 install -r requirements.txt
cp .env.example .env
```

Edit `.env` and fill in your bot token and chat ID:

```
TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
TELEGRAM_CHAT_ID=123456789
```

### 4. Start Claude Code

```bash
chmod +x start.sh
./start.sh
```

This creates a tmux session and launches Claude Code inside it. To peek at what Claude is doing:

```bash
tmux attach -t claude    # see the session
# Press Ctrl+B then D to detach (leave it running)
```

**Optional: `claude` shortcut.** Add this to your `~/.bashrc` or `~/.zshrc` so you can type `claude` to jump into your session:

```bash
claude() {
  tmux attach -t claude 2>/dev/null || \
    (tmux new-session -d -s claude -x 200 -y 50 && \
     tmux send-keys -t claude 'claude --dangerously-skip-permissions' Enter && \
     sleep 2 && \
     tmux attach -t claude)
}
```

Attaches to an existing session or creates a new one. One command. To remove it later, delete those lines and run `source ~/.zshrc`.

### 5. Start the bot

In a separate terminal:

```bash
# Load your env vars
export $(cat .env | xargs)
python3 bot.py
```

Now open Telegram and text your bot. Try: "what files are in the current directory?"

## Keep it running

You probably want the bot to survive reboots and stay running when you close the terminal.

### Mac (LaunchAgent)

```bash
# Edit the paths and tokens in this plist, then:
cp claude-bot.plist ~/Library/LaunchAgents/com.you.claude-bot.plist
launchctl load ~/Library/LaunchAgents/com.you.claude-bot.plist
```

### Linux (systemd)

```bash
cp claude-bot.service ~/.config/systemd/user/
# Edit the paths and tokens in the service file
systemctl --user enable --now claude-bot
```

### Windows (WSL)

Run inside a WSL tmux session:

```bash
tmux new -s bot
export $(cat .env | xargs)
python3 bot.py
# Ctrl+B, D to detach
```

## Drop the subscription: use local models

Instead of paying Anthropic, point Claude Code at a local model running on your hardware.

1. Install [LMStudio](https://lmstudio.ai/) or [Ollama](https://ollama.com/)
2. Load a model (start with something in the 7-35B range)
3. Set these env vars before running `start.sh`:

```bash
export ANTHROPIC_BASE_URL=http://localhost:1234    # LMStudio default
export ANTHROPIC_AUTH_TOKEN=lmstudio               # any non-empty string
```

LMStudio serves the Anthropic Messages API natively. Claude Code connects to it like it's talking to Anthropic's servers, but inference runs locally. Zero cost after hardware.

**Hardware requirements:**
- 7B model: 16GB+ RAM or 8GB+ VRAM
- 35B model: 64GB+ RAM or 24GB+ VRAM
- 70B+ model: 128GB+ RAM or multiple GPUs

Start small. A 7-9B model handles simple tasks. Scale up as needed.

## Security

**The `--dangerously-skip-permissions` flag is dangerous.** It lets Claude run any command without asking. On a dedicated machine with nothing important on it, that's fine. On your daily driver, think carefully.

Safer alternatives:
- **Dedicated user account** -- create a separate OS user with limited access
- **Docker container** -- run Claude Code in a container with only your project mounted
- **`--permissionMode plan`** -- Claude plans actions but asks before executing
- **`allowedTools`** -- whitelist specific tools in `.claude/settings.json`

**The bot only accepts messages from your `TELEGRAM_CHAT_ID`.** This is critical. Telegram bots are publicly discoverable. Without this check, anyone who finds your bot's username can execute commands on your machine.

## Next steps

Once this works, the upgrades that matter:

- **JSONL reading** -- Claude Code writes `.jsonl` transcripts. Parse those instead of scraping tmux for more reliable output.
- **Inline buttons** -- Add Approve/Reject/Tweak buttons using Telegram's `InlineKeyboardMarkup`. Now you've got approval workflows.
- **Scheduled tasks** -- Cron/LaunchAgent/systemd timers to run things on a schedule.
- **Multiple agents** -- Second tmux session + second Telegram bot = two agents on one machine.
- **Local models** -- Drop the Claude subscription entirely with LMStudio or Ollama.

## License

MIT. Do whatever you want with it.
