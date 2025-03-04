from flask import Blueprint, request, jsonify
from .helpers import write_to_google_sheet, store_and_process_message

app = Blueprint("routes", __name__)


@app.route("/webhook", methods=["GET"])
def verify_webhook():
    #FIXME: This should be in the config file
    VERIFY_TOKEN = "INSERT_YOUR_TOKEN_HERE"
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    else:
        return "Verification failed", 403


@app.route("/webhook", methods=["POST"])
def handle_messages():
    data = request.get_json()
    try:
        entry = data.get("entry", [])[0]
        changes = entry.get("changes", [])[0]
        messages = changes.get("value", {}).get("messages", [])
        for message in messages:
            sender = message.get("from")
            timestamp = message.get("timestamp")
            text = message.get("text", {}).get("body")

            month, row = store_and_process_message(sender, timestamp, text)
            write_to_google_sheet(month, row)

            return jsonify({"status": "success"}), 200

    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500
