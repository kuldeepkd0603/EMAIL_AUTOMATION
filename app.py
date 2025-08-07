from flask import Flask, request, redirect, send_file, jsonify
from db import campaigns, stages, users, rules
from datetime import datetime

app = Flask(__name__)

def safe_stage_param():
    stage_arg = request.args.get("stage", "")
    try:
        return int(stage_arg)
    except (ValueError, TypeError):
        return 0  # Fallback stage

@app.route('/track/open')
def track_open():
    email = request.args.get("email")
    stage = safe_stage_param()
    if email:
        stages.update_one({"email": email, "stage": stage}, {"$set": {"opened": True}})
        campaigns.update_one({"email": email}, {"$set": {"last_opened": datetime.utcnow()}})
    return send_file("pixel.png", mimetype="image/png")

@app.route('/track/click')
def track_click():
    email = request.args.get("email")
    stage = safe_stage_param()
    target = request.args.get("target", "https://default-redirect.com")
    if email:
        stages.update_one({"email": email, "stage": stage}, {"$set": {"clicked": True}})
        campaigns.update_one({"email": email}, {"$set": {"last_clicked": datetime.utcnow()}})
    return redirect(target)

@app.route('/unsubscribe')
def unsubscribe():
    email = request.args.get("email")
    if email:
        users.update_one({"email": email}, {"$set": {"unsubscribed": True}})
        campaigns.update_one({"email": email}, {"$set": {"status": "unsubscribed"}})
    return "You have been unsubscribed."

@app.route('/upload_rules', methods=['POST'])
def upload_rules():
    data = request.get_json()
    user_id = data.get("user_id")
    rules_data = data.get("rules", [])
    if user_id and isinstance(rules_data, list):
        rules.update_one({"user_id": user_id}, {"$set": {"rules": rules_data}}, upsert=True)
        return jsonify({"status": "Rules uploaded successfully"})
    return jsonify({"error": "Invalid input"}), 400

if __name__ == '__main__':
    app.run(debug=True)
