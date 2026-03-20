#!/usr/bin/env python3
"""Minimal Telegram-to-tmux bridge for Claude Code.

Receives messages from Telegram, types them into a tmux session
where Claude Code is running, waits for output, sends it back.

Setup:
    1. Create a Telegram bot via @BotFather
    2. Get your chat ID via @userinfobot
    3. Set env vars: TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
    4. Start Claude Code in tmux: ./start.sh
    5. Run this bot: python3 bot.py
"""

import os
import time
import subprocess
import threading

import requests

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]  # your personal chat ID
TMUX_SESSION = os.environ.get("TMUX_SESSION", "claude")
API = f"https://api.telegram.org/bot{BOT_TOKEN}"
last_update_id = 0


def tg(method, **kw):
    """Call a Telegram Bot API method."""
    r = requests.post(f"{API}/{method}", data=kw, timeout=30)
    return r.json()


def send(text):
    """Send a message to Telegram, splitting if needed."""
    for i in range(0, len(text), 4000):
        tg("sendMessage", chat_id=CHAT_ID, text=text[i : i + 4000])


def tmux_send(text):
    """Type text into the tmux session."""
    subprocess.run(["tmux", "send-keys", "-t", TMUX_SESSION, text, "Enter"])


def tmux_capture():
    """Grab current tmux pane content."""
    r = subprocess.run(
        ["tmux", "capture-pane", "-t", TMUX_SESSION, "-p", "-S", "-50"],
        capture_output=True,
        text=True,
    )
    return r.stdout.strip()


def poll_output(before_snapshot):
    """Wait for Claude to finish, then send the new output."""
    time.sleep(3)  # give Claude a moment to start
    stable_count = 0
    last_content = ""

    while stable_count < 3:
        time.sleep(2)
        current = tmux_capture()
        if current == last_content:
            stable_count += 1
        else:
            stable_count = 0
            last_content = current

    # Find what's new since we sent the command
    new_lines = []
    before_lines = set(before_snapshot.splitlines())
    for line in last_content.splitlines():
        if line not in before_lines:
            new_lines.append(line)

    if new_lines:
        send("\n".join(new_lines[-100:]))  # last 100 lines max
    else:
        send("(no new output detected)")


def main():
    global last_update_id
    send("Bot online. Claude Code is listening.")
    print(f"Bot started. Listening for messages from chat {CHAT_ID}...")

    while True:
        try:
            resp = tg("getUpdates", offset=last_update_id + 1, timeout=30)
            for update in resp.get("result", []):
                last_update_id = update["update_id"]
                msg = update.get("message", {})
                text = msg.get("text", "")
                chat = msg.get("chat", {}).get("id")

                # SECURITY: Only accept messages from your chat ID
                if str(chat) != str(CHAT_ID) or not text:
                    continue

                print(f"Received: {text[:80]}...")

                # Capture before state, send command, watch for output
                before = tmux_capture()
                tmux_send(text)
                threading.Thread(
                    target=poll_output, args=(before,), daemon=True
                ).start()

        except KeyboardInterrupt:
            print("\nShutting down.")
            break
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()
