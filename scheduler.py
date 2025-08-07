from datetime import datetime, timedelta, timezone
from email_sender import send_mail
from db import campaigns, stages, users, rules

now = datetime.now(timezone.utc)

for user in users.find({"unsubscribed": {"$ne": True}}):
    email = user["email"]
    name = user.get("name", "there")
    user_id = user.get("user_id", "default")
    rule_set = rules.find_one({"user_id": user_id})
    
    if not rule_set:
        continue

    campaign = campaigns.find_one({"email": email})
    current_stage = campaign["current_stage"] if campaign else -1

    # Next stage = current_stage + 1
    next_stage = current_stage + 1
    rule = next((r for r in rule_set["rules"] if r["stage"] == next_stage), None)
    
    if not rule:
        continue  # No more stages to process

    condition = rule["condition"]
    wait_minutes = rule.get("wait_minutes", 0)
    max_count = rule.get("max_count", 1)

    subject = rule["subject"].replace("{{name}}", name)
    content = rule["content"].replace("{{name}}", name)

    # Check last stage interaction
    if current_stage >= 0:
        last_stage_doc = stages.find_one({"email": email, "stage": current_stage})
    else:
        last_stage_doc = None

    should_send = False

    if condition == "initial" and current_stage == -1:
        should_send = True
    elif last_stage_doc:
        if condition == "not_opened" and not last_stage_doc.get("opened", False):
            should_send = True
        elif condition == "opened" and last_stage_doc.get("opened", False):
            should_send = True
        elif condition == "not_clicked" and not last_stage_doc.get("clicked", False):
            should_send = True
        elif condition == "clicked" and last_stage_doc.get("clicked", False):
            should_send = True

        if should_send:
            last_sent = last_stage_doc.get("sent_at")
            if last_sent and last_sent.tzinfo is None:
                last_sent = last_sent.replace(tzinfo=timezone.utc)

            if last_sent and now - last_sent < timedelta(minutes=wait_minutes):
                should_send = False  # Wait time not passed yet
    else:
        # If there's no stage doc for the last stage, skip this user
        if condition != "initial":
            continue

    if not should_send:
        continue

    # Double-check unsubscribe status before sending
    if users.find_one({"email": email}).get("unsubscribed"):
        continue

    send_time = send_mail(email, name, next_stage, subject, content)

    if not campaign:
        campaigns.insert_one({
            "email": email,
            "current_stage": next_stage,
            "last_sent": send_time,
            "status": "active"
        })
    else:
        campaigns.update_one(
            {"email": email},
            {"$set": {
                "current_stage": next_stage,
                "last_sent": send_time
            }}
        )

    stages.update_one(
        {"email": email, "stage": next_stage},
        {"$set": {
            "opened": False,
            "clicked": False,
            "sent_at": send_time
        }},
        upsert=True
    )
