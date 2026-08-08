"""
telegram_listener.py
Always-on Telegram control listener

Commands:
 /help
 /status
 /run
 /report
 /train
"""

import logging
import os
import time

import requests


# ==========================================================
# CONFIG
# ==========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_REPOSITORY = os.getenv("GITHUB_REPOSITORY")

TELEGRAM_API = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
)

GITHUB_API = "https://api.github.com"


# ==========================================================
# LOGGING
# ==========================================================

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)s | %(message)s"
)

logger = logging.getLogger(__name__)


# ==========================================================
# VALIDATE CONFIG
# ==========================================================

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing")

if not CHAT_ID:
    raise RuntimeError("CHAT_ID is missing")

if not GITHUB_TOKEN:
    raise RuntimeError("GITHUB_TOKEN is missing")

if not GITHUB_REPOSITORY:
    raise RuntimeError("GITHUB_REPOSITORY is missing")


# ==========================================================
# SEND TELEGRAM MESSAGE
# ==========================================================

def send_message(chat_id, text):

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
# GET TELEGRAM UPDATES
# ==========================================================

def get_updates(offset):

    try:

        response = requests.get(
            f"{TELEGRAM_API}/getUpdates",
            params={
                "offset": offset,
                "timeout": 50
            },
            timeout=60
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

    except requests.exceptions.Timeout:

        return []

    except Exception as e:

        logger.error(
            f"Telegram getUpdates failed: {e}"
        )

        return []


# ==========================================================
# TRIGGER GITHUB WORKFLOW
# ==========================================================

def trigger_workflow(workflow_file):

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

def process_command(chat_id, text):

    command = text.strip().split()[0].lower()

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
    # RUN
    # ------------------------------------------------------

    if command == "/run":

        send_message(
            chat_id,
            "📈 Starting AI NSE stock prediction..."
        )

        success = trigger_workflow(
            "predict.yml"
        )

        if success:

            send_message(
                chat_id,
                "✅ Prediction workflow started."
            )

        else:

            send_message(
                chat_id,
                "❌ Failed to start prediction workflow."
            )

        return


    # ------------------------------------------------------
    # REPORT
    # ------------------------------------------------------

    if command == "/report":

        send_message(
            chat_id,
            "📊 Starting AI NSE day-end report..."
        )

        success = trigger_workflow(
            "day_end.yml"
        )

        if success:

            send_message(
                chat_id,
                "✅ Day-end report workflow started."
            )

        else:

            send_message(
                chat_id,
                "❌ Failed to start day-end workflow."
            )

        return


    # ------------------------------------------------------
    # TRAIN
    # ------------------------------------------------------

    if command == "/train":

        send_message(
            chat_id,
            "🤖 Starting AI NSE model training..."
        )

        success = trigger_workflow(
            "train_model.yml"
        )

        if success:

            send_message(
                chat_id,
                "✅ Model training workflow started."
            )

        else:

            send_message(
                chat_id,
                "❌ Failed to start training workflow."
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
# MAIN LISTENER
# ==========================================================

def main():

    logger.info(
        "Telegram listener started."
    )

    offset = None

    while True:

        try:

            updates = get_updates(
                offset
            )

            for update in updates:

                update_id = update.get(
                    "update_id"
                )

                if update_id is None:
                    continue

                # Confirm update
                offset = update_id + 1

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

                logger.info(
                    f"Command received: {text}"
                )

                process_command(
                    chat_id,
                    text
                )

        except Exception as e:

            logger.exception(
                f"Listener error: {e}"
            )

            time.sleep(5)


# ==========================================================
# ENTRY
# ==========================================================

if __name__ == "__main__":

    main()
