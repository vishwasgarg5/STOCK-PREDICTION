```python
"""
telegram_commands.py

Telegram control for AI NSE Stock Prediction System.

Commands:

/run      -> Run prediction workflow
/train    -> Run model training workflow
/report   -> Run day-end report workflow
/status   -> Show system status
/help     -> Show available commands
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


TELEGRAM_API = (
    f"https://api.telegram.org/bot{BOT_TOKEN}"
)

GITHUB_API = "https://api.github.com"


# ==========================================================
# WORKFLOWS
# ==========================================================

WORKFLOWS = {

    "/run": {
        "file": "predict.yml",
        "message": (
            "📈 Prediction workflow triggered."
        )
    },

    "/train": {
        "file": "train_model.yml",
        "message": (
            "🤖 Model training workflow triggered."
        )
    },

    "/report": {
        "file": "day_end.yml",
        "message": (
            "📊 Day-end report workflow triggered."
        )
    },

}


# ==========================================================
# TELEGRAM REQUEST
# ==========================================================

def telegram_request(
    method,
    params=None
):

    url = (
        f"{TELEGRAM_API}/{method}"
    )

    try:

        response = requests.get(
            url,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if not data.get("ok"):

            logger.error(
                f"Telegram API error: {data}"
            )

            return None

        return data

    except Exception as e:

        logger.error(
            f"Telegram request failed: {e}"
        )

        return None


# ==========================================================
# SEND TELEGRAM MESSAGE
# ==========================================================

def send_message(
    chat_id,
    text
):

    url = (
        f"{TELEGRAM_API}/sendMessage"
    )

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
# GET UPDATES
# ==========================================================

def get_updates():

    data = telegram_request(
        "getUpdates"
    )

    if not data:

        return []

    updates = data.get(
        "result",
        []
    )

    logger.info(
        f"Telegram updates received: "
        f"{len(updates)}"
    )

    return updates


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
    # WORKFLOW COMMAND
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
                "❌ Failed to trigger workflow.\n\n"
                "Please check GitHub Actions."
            )

        return


    # ------------------------------------------------------
    # UNKNOWN COMMAND
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

    updates = get_updates()

    if not updates:

        logger.info(
            "No Telegram commands."
        )

        return


    # ------------------------------------------------------
    # PROCESS UPDATES
    # ------------------------------------------------------

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
        # SECURITY CHECK
        # --------------------------------------------------

        if (
            str(chat_id)
            != str(CHAT_ID)
        ):

            logger.warning(
                f"Unauthorized chat ID: "
                f"{chat_id}"
            )

            continue


        logger.info(
            f"Command received: "
            f"{text}"
        )


        # --------------------------------------------------
        # PROCESS COMMAND
        # --------------------------------------------------

        process_command(
            chat_id,
            text
        )


        # --------------------------------------------------
        # ACKNOWLEDGE UPDATE
        # --------------------------------------------------

        if update_id is not None:

            telegram_request(
                "getUpdates",
                {
                    "offset":
                        update_id + 1
                }
            )


# ==========================================================
# ENTRY POINT
# ==========================================================

if __name__ == "__main__":

    main()
```
