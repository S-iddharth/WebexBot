from flask import Flask, request, jsonify
import csv
import smtplib
from email.message import EmailMessage
import requests
import os
from datetime import datetime
from services.logic import load_user_emails, load_responses, update_response

app = Flask(__name__)

WEBEX_BOT_TOKEN = "<YOUR_WEBEX_BOT_TOKEN>"
SMTP_SERVER = "smtp.yourdomain.com"
SMTP_PORT = 587
SMTP_USER = "noreply@yourdomain.com"
SMTP_PASSWORD = "yourpassword"
FROM_EMAIL = "noreply@yourdomain.com"

user_email_map = load_user_emails()
user_responses = load_responses()

def send_webex_msg(email):
    url = "https://webexapis.com/v1/messages"
    headers = {
        "Authorization": f"Bearer {WEBEX_BOT_TOKEN}",
        "Content-Type": "application/json"
    }
    payload = {
        "toPersonEmail": email,
        "text": "Hi! You're still connected to the old VPN. Please switch to the new SASE VPN. Contact IT if you need help."
    }
    r = requests.post(url, headers=headers, json=payload)
    return r.status_code == 200

def send_email(to_email):
    msg = EmailMessage()
    msg["Subject"] = "Action Required: Switch to SASE VPN"
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg.set_content("Hi, you're still using the legacy VPN. Please migrate to the SASE VPN by end of this week.")
    with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.send_message(msg)

@app.route("/webhook", methods=["POST"])
def handle_webhook():
    data = request.json
    username = data.get("username")
    if not username:
        return jsonify({"error": "Username not provided"}), 400

    email = user_email_map.get(username)
    if not email:
        return jsonify({"error": "User not found"}), 404

    response_data = user_responses.get(username)
    should_send = False

    if not response_data:
        should_send = True
        counter = 2  # Allow 2 follow-ups
    elif response_data["counter"] > 0:
        should_send = True
        counter = response_data["counter"] - 1
    else:
        should_send = False

    if should_send:
        try:
            send_webex_msg(email)
            send_email(email)
            update_response(username, counter)
            return jsonify({"message": "Notification sent"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500
    else:
        return jsonify({"message": "User already notified enough times"}), 200

if __name__ == "__main__":
    os.makedirs("logs", exist_ok=True)
    app.run(host="0.0.0.0", port=5000)
