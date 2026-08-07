"""
telegram_commands.py

Telegram control for AI NSE Stock Prediction System.
"""

import os
import logging
import requests


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# CONFIGURATION
# ==========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

if not CHAT_ID:
    raise RuntimeError("CHAT_ID is missing")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is missing")

if not GITHUB_REPOSITORY:
    raise RuntimeError("GITHUB_REPOSITORY is missing")


TELEGRAM_API = f"https://api.telegram.org/bot{BOT_TOKEN}"

GITHUB_API = "https://api.github.com"


# ==========================================================
# WORKFLOWS
# ==========================================================

WORKFLOWS = {

    "/run": {
        "file": "predict.yml",
        "message": "📈 Prediction workflow triggered."
    },

    "/train": {
        "file": "train_model.yml",
        "message": "🤖 Model training workflow triggered."
    },

    "/report": {
        "file": "day_end.yml",
        "message": "📊 Day-end report workflow triggered."
    },

}


# ==========================================================
# TELEGRAM API
# ==========================================================

def telegram_get_updates(offset=None):

    params = {
        "timeout": 10
    }

    if offset is not None:
        params["offset"] = offset

    try:

        response = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):

            logger.error(
                f"Telegram API error: {data}"
            )

            return []

        return data.get(
            "result",
            []
        )

    except Exception as e:

        logger.error(
            f"Telegram getUpdates failed: {e}"
        )

        return []


# ==========================================================
# DELETE / CLEAR OLD UPDATES
# ==========================================================

def clear_updates(updates):

    if not updates:
        return

    latest_update_id = max(
        update["update_id"]
        for update in updates
        if "update_id" in update
    )

    offset = latest_update_id + 1

    logger.info(
        f"Clearing Telegram updates through "
        f"update_id {latest_update_id}"
    )

    try:

        requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params={
                "offset": offset,
                "timeout": 1
            },
            timeout=10
        )

    except Exception as e:

        logger.warning(
            f"Could not clear Telegram updates: {e}"
        )


# ==========================================================
# SEND MESSAGE
# ==========================================================

def send_message(
    chat_id,
    text
):

    try:

        response = requests.post(
            f"{TELEGRAM_API}/sendMessage",
            data={
                "chat_id": chat_id,
                "text": text
            },
            timeout=30
        )

        response.raise_for_status()

        logger.info(
            "Telegram response sent."
        )

        return True

    except Exception as e:

        logger.error(
            f"Telegram send failed: {e}"
        )

        return False


# ==========================================================
# TRIGGER GITHUB WORKFLOW
# ==========================================================

def trigger_workflow(
    workflow_file
):

    url = (
        f"{GITHUB_API}/repos/"
        f"{GITHUB_REPOSITORY}/actions/"
        f"workflows/"
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

    try:

        response = requests.post(
            url,
            headers=headers,
            json={
                "ref": "main"
            },
            timeout=30
        )

        if response.status_code == 204:

            logger.info(
                f"Workflow triggered: "
                f"{workflow_file}"
            )

            return True

        logger.error(
            f"GitHub API error "
            f"{response.status_code}: "
            f"{response.text}"
        )

        return False

    except Exception as e:

        logger.error(
            f"GitHub workflow error: {e}"
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
        "Start AI model training.\n\n"

        "📊 /report\n"
        "Run day-end predicted vs actual report.\n\n"

        "ℹ️ /status\n"
        "Show system status.\n\n"

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

    command = (
        command
        .strip()
        .lower()
        .split()[0]
    )

    logger.info(
        f"Processing command: {command}"
    )

    # ------------------------------------------------------
    # HELP
    # ------------------------------------------------------

    if command == "/help":

        send_message(
            chat_id,
            help_message()
        )

        return


    # ------------------------------------------------------
    # STATUS
    # ------------------------------------------------------

    if command == "/status":

        send_message(
            chat_id,
            status_message()
        )

        return


    # ------------------------------------------------------
    # WORKFLOW COMMANDS
    # ------------------------------------------------------

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
                "❌ Failed to trigger workflow."
            )

        return


    # ------------------------------------------------------
    # UNKNOWN
    # ------------------------------------------------------

    send_message(
        chat_id,
        "❓ Unknown command.\n\n"
        "Use /help."
    )


# ==========================================================
# MAIN
# ==========================================================

def main():

    logger.info(
        "Telegram controller started."
    )

    updates = telegram_get_updates()

    if not updates:

        logger.info(
            "No Telegram commands."
        )

        return


    logger.info(
        f"Telegram updates received: "
        f"{len(updates)}"
    )


    # ======================================================
    # FIND ONLY THE LATEST VALID MESSAGE
    # ======================================================

    latest_message = None
    latest_update_id = None

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

        # --------------------------------------------------
        # SECURITY
        # --------------------------------------------------

        if str(chat_id) != str(CHAT_ID):

            logger.warning(
                f"Unauthorized chat ID: "
                f"{chat_id}"
            )

            continue

        latest_message = {
            "chat_id": chat_id,
            "text": text
        }

        latest_update_id = update_id


    # ======================================================
    # CLEAR ALL RECEIVED UPDATES
    # ======================================================

    clear_updates(updates)


    # ======================================================
    # PROCESS ONLY LATEST COMMAND
    # ======================================================

    if latest_message is None:

        logger.info(
            "No valid Telegram command."
        )

        return


    logger.info(
        f"Command received: "
        f"{latest_message['text']}"
    )

    process_command(
        latest_message["chat_id"],
        latest_message["text"]
    )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()
