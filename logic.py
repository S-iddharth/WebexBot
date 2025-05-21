import csv
import os
from datetime import datetime

RESPONSE_FILE = "logs/response_file.csv"

def load_user_emails(file="users.csv"):
    mapping = {}
    with open(file, mode='r') as file:
        reader = csv.DictReader(file)
        for row in reader:
            mapping[row['username']] = row['email']
    return mapping

def load_responses():
    responses = {}
    if not os.path.exists(RESPONSE_FILE):
        return responses
    with open(RESPONSE_FILE, mode='r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            responses[row['username']] = {"counter": int(row['counter']), "last_sent": row['last_sent']}
    return responses

def update_response(username, counter):
    responses = load_responses()
    responses[username] = {"counter": counter, "last_sent": datetime.now().isoformat()}
    with open(RESPONSE_FILE, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=["username", "counter", "last_sent"])
        writer.writeheader()
        for user, data in responses.items():
            writer.writerow({"username": user, "counter": data["counter"], "last_sent": data["last_sent"]})
