"""
telegram_commands.py

Telegram control for AI NSE Stock Prediction System.

Commands:

/run      -> Run prediction workflow
/train    -> Run model training workflow
/report   -> Run day-end report workflow
/status   -> Show available workflows
/help     -> Show commands
"""

import os
import logging
import requests


# ==========================================================
# CONFIGURATION
# ==========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is missing")

if not GITHUB_REPOSITORY:
    raise RuntimeError("GITHUB_REPOSITORY is missing")


TELEGRAM_API = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
)

GITHUB_API = "https://api.github.com"


# ==========================================================
# WORKFLOW NAMES
# ==========================================================

WORKFLOWS = {

    "/run": {
        "file": "predict.yml",
        "message": (
            "🚀 AI Stock Prediction workflow "
            "has been triggered."
        )
    },

    "/train": {
        "file": "train_model.yml",
        "message": (
            "🤖 AI Model Training workflow "
            "has been triggered."
        )
    },

    "/report": {
        "file": "day_end.yml",
        "message": (
            "📊 AI Day-End Report workflow "
            "has been triggered."
        )
    },

}


# ==========================================================
# TELEGRAM SEND
# ==========================================================

def send_message(chat_id, text):

    url = f"{TELEGRAM_API}/sendMessage"

    try:

        response = requests.post(
            url,
            data={
                "chat_id": chat_id,
                "text": text
            },
            timeout=30
        )

        response.raise_for_status()

        return True

    except Exception as e:

        logging.error(
            f"Telegram send error: {e}"
        )

        return False


# ==========================================================
# GET TELEGRAM UPDATES
# ==========================================================

def get_updates():

    url = f"{TELEGRAM_API}/getUpdates"

    try:

        response = requests.get(
            url,
            params={
                "timeout": 10
            },
            timeout=20
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):
            return []

        return data.get(
            "result",
            []
        )

    except Exception as e:

        logging.error(
            f"Telegram update error: {e}"
        )

        return []


# ==========================================================
# TRIGGER GITHUB WORKFLOW
# ==========================================================

def trigger_workflow(workflow_file):

    url = (
        f"{GITHUB_API}/repos/"
        f"{GITHUB_REPOSITORY}/actions/workflows/"
        f"{workflow_file}/dispatches"
    )

    headers = {
        "Authorization":
            f"Bearer {GITHUB_TOKEN}",

        "Accept":
            "application/vnd.github+json",

        "X-GitHub-Api-Version":
            "2022-11-28"
    }

    payload = {
        "ref": "main"
    }

    try:

        response = requests.post(
            url,
            headers=headers,
            json=payload,
            timeout=30
        )

        if response.status_code == 204:

            logging.info(
                f"Workflow triggered: {workflow_file}"
            )

            return True

        logging.error(
            f"GitHub error {response.status_code}: "
            f"{response.text}"
        )

        return False

    except Exception as e:

        logging.error(
            f"Workflow trigger error: {e}"
        )

        return False


# ==========================================================
# HELP
# ==========================================================

def help_message():

    return (
        "🤖 AI NSE CONTROL BOT\n\n"

        "Available commands:\n\n"

        "📈 /run\n"
        "Run today's AI stock prediction.\n\n"

        "🤖 /train\n"
        "Start model self-training.\n\n"

        "📊 /report\n"
        "Run the day-end predicted vs actual report.\n\n"

        "ℹ️ /status\n"
        "Show available workflows.\n\n"

        "❓ /help\n"
        "Show this help message."
    )


# ==========================================================
# STATUS
# ==========================================================

def status_message():

    return (
        "🟢 AI NSE SYSTEM\n\n"

        "Scheduled workflows:\n\n"

        "📈 Prediction\n"
        "Monday-Friday\n"
        "09:00 IST\n\n"

        "📊 Day-End Report\n"
        "Monday-Friday\n"
        "16:00 IST\n\n"

        "🤖 Model Training\n"
        "Monday-Friday\n"
        "21:00 IST\n\n"

        "Telegram control: ACTIVE"
    )


# ==========================================================
# PROCESS COMMAND
# ==========================================================

def process_command(
    chat_id,
    command
):

    command = command.strip().lower()

    logging.info(
        f"Telegram command: {command}"
    )

    # --------------------------------------
    # HELP
    # --------------------------------------

    if command == "/help":

        send_message(
            chat_id,
            help_message()
        )

        return

    # --------------------------------------
    # STATUS
    # --------------------------------------

    if command == "/status":

        send_message(
            chat_id,
            status_message()
        )

        return

    # --------------------------------------
    # WORKFLOW COMMANDS
    # --------------------------------------

    if command in WORKFLOWS:

        workflow = WORKFLOWS[command]

        send_message(
            chat_id,
            "⏳ Triggering GitHub Actions..."
        )

        success = trigger_workflow(
            workflow["file"]
        )

        if success:

            send_message(
                chat_id,
                "✅ "
                + workflow["message"]
                + "\n\n"
                "GitHub Actions has started."
            )

        else:

            send_message(
                chat_id,
                "❌ Failed to trigger workflow.\n\n"
                "Check GitHub Actions and token permissions."
            )

        return

    # --------------------------------------
    # UNKNOWN COMMAND
    # --------------------------------------

    send_message(
        chat_id,
        "❓ Unknown command.\n\n"
        "Use /help to see available commands."
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        )
    )

    updates = get_updates()

    if not updates:

        logging.info(
            "No Telegram commands."
        )

        return

    for update in updates:

        update_id = update.get(
            "update_id"
        )

        message = update.get(
            "message"
        )

        if not message:
            continue

        chat = message.get(
            "chat",
            {}
        )

        chat_id = chat.get(
            "id"
        )

        text = message.get(
            "text",
            ""
        )

        if not chat_id or not text:
            continue

        # ----------------------------------
        # SECURITY
        # ----------------------------------
        #
        # Only respond to the configured
        # Telegram chat ID.
        #

        allowed_chat_id = os.getenv(
            "CHAT_ID"
        )

        if (
            allowed_chat_id
            and str(chat_id)
            != str(allowed_chat_id)
        ):

            logging.warning(
                f"Unauthorized Telegram chat: "
                f"{chat_id}"
            )

            continue

        process_command(
            chat_id,
            text
        )

        # ----------------------------------
        # Mark update as processed
        # ----------------------------------

        if update_id is not None:

            requests.get(
                f"{TELEGRAM_API}/getUpdates",
                params={
                    "offset": update_id + 1
                },
                timeout=20
            )


if __name__ == "__main__":

    main()
