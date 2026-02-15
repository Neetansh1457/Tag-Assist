from flask import Flask, request, render_template, session
import joblib
import numpy as np
import uuid
from datetime import datetime
import random
import os



embedding_model = None

def get_embedding_model():
    global embedding_model

    if embedding_model is None:
        from sentence_transformers import SentenceTransformer
        print("Loading MiniLM model...")
        embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

    return embedding_model


app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "fallback-dev-key")

# Load models
behavior_model = joblib.load("behavior_model.pkl")
text_model = joblib.load("text_model.pkl")
# embedding_model = joblib.load("embedding_model.pkl")

#
FEATURE_NAMES = [
    "order_velocity",
    "device_changes_7d",
    "ip_changes_7d",
    "unpaid_ratio",
    "risky_category_flag"
]


# -------- Normalize Annotation --------
def normalize_annotation(text):
    replacements = {
        "order vel": "high order velocity observed",
        "card vel": "elevated card usage velocity",
        "ip chg": "frequent IP address changes",
        "dev chg": "multiple device changes detected",
        ";": ". ",
        "//": " "
    }

    text = text.lower()
    for k, v in replacements.items():
        text = text.replace(k, v)

    return text


# -------- Random Case --------
def generate_random_case():
    return {
        "order_velocity": round(random.uniform(2, 12), 2),
        "device_changes": random.randint(0, 4),
        "ip_changes": random.randint(0, 3),
        "unpaid_ratio": round(random.uniform(0.0, 0.8), 2),
        "risky_flag": random.choice([0, 1]),
        "annotation": random.choice([
            "order vel; card vel; multiple device changes observed.",
            "ip chg detected with elevated order velocity.",
            "high unpaid ratio with risky category purchases.",
            "order vel spike; dev chg; possible coordinated misuse.",
            "moderate activity increase but no strong cluster linkage.",
            "card vel; ip chg; prior suspicious activity noted."
        ])
    }


# -------- Feature Importance --------
def get_feature_importance():
    importances = behavior_model.feature_importances_
    sorted_idx = np.argsort(importances)[::-1]

    return [
        (FEATURE_NAMES[i], float(round(float(importances[i]), 3)))
        for i in sorted_idx
    ]


# -------- Main Route --------
@app.route("/", methods=["GET", "POST"])
def home():

    if "case_history" not in session:
        session["case_history"] = []

    if request.method == "POST":

        request_id = str(uuid.uuid4())[:8]
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        order_velocity = float(request.form["order_velocity"])
        device_changes = int(request.form["device_changes"])
        ip_changes = int(request.form["ip_changes"])
        unpaid_ratio = float(request.form["unpaid_ratio"])
        risky_flag = int(request.form["risky_flag"])
        threshold = float(request.form["threshold"])
        annotation = request.form["annotation"]

        clean_annotation = normalize_annotation(annotation)

        # Behavioral Prediction
        X_behavior = np.array([[
            order_velocity,
            device_changes,
            ip_changes,
            unpaid_ratio,
            risky_flag
        ]])

        behavior_score = behavior_model.predict_proba(X_behavior)[0][1]

        # Text Prediction
        model = get_embedding_model()
        embedding = model.encode([clean_annotation])
        text_score = text_model.predict_proba(embedding)[0][1]

        final_score = 0.3 * behavior_score + 0.7 * text_score
        decision = "APPROVE" if final_score > threshold else "REJECT"

        # Store in session history
        session["case_history"].append({
            "id": str(request_id),
            "score": float(round(float(final_score), 3)),
            "decision": str(decision)
        })

        session.modified = True

        # Auto approval rate
        total_cases = len(session["case_history"])
        approved_cases = sum(1 for c in session["case_history"] if c["decision"] == "APPROVE")
        approval_rate = round((approved_cases / total_cases) * 100, 2)

        return render_template(
            "index.html",
            behavior_score=round(behavior_score, 3),
            text_score=round(text_score, 3),
            final_score=round(final_score, 3),
            decision=decision,
            threshold=threshold,
            request_id=request_id,
            timestamp=timestamp,
            feature_importance=get_feature_importance(),
            case_history=session["case_history"],
            approval_rate=approval_rate,
            case_data=generate_random_case()
        )

    return render_template(
        "index.html",
        threshold=0.5,
        case_data=generate_random_case(),
        case_history=session["case_history"],
        approval_rate=0
    )


if __name__ == "__main__":
    app.run()
