from flask import Flask, request, jsonify
import os
import requests
from datetime import datetime

app = Flask(__name__)

NOTION_TOKEN = os.environ.get("NOTION_TOKEN")
DATABASE_ID = os.environ.get("NOTION_DATABASE_ID")

HEADERS = {
    "Authorization": f"Bearer {NOTION_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2022-06-28",
}


def create_task(title, task_type="Pro", status="À faire", date=None):
    if date is None:
        date = datetime.now().strftime("%Y-%m-%d")

    data = {
        "parent": {"database_id": DATABASE_ID},
        "properties": {
            "Tache": {"title": [{"text": {"content": title}}]},
            "Type": {"select": {"name": task_type}},
            "Statut": {"select": {"name": status}},
            "Date": {"date": {"start": date}},
        },
    }

    response = requests.post(
        "https://api.notion.com/v1/pages", headers=HEADERS, json=data
    )

    return response.status_code, response.json()


@app.route("/", methods=["GET"])
def health():
    return "Notion Assistant is running.", 200


@app.route("/add-task", methods=["POST"])
def add_task():
    req_data = request.get_json()
    title = req_data.get("title")
    task_type = req_data.get("type", "Pro")
    status = req_data.get("status", "À faire")
    date = req_data.get("date")

    if not title:
        return jsonify({"error": "Missing task title"}), 400

    code, response = create_task(title, task_type, status, date)
    return jsonify({"notion_status": code, "response": response}), code


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
