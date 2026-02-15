from flask import Flask, request, render_template
import joblib
import numpy as np
import uuid
from datetime import datetime
import random

app = Flask(__name__)

# -------- Load Models --------
behavior_model = joblib.load("behavior_model.pkl")
text_model = joblib.load("text_model.pkl")
embedding_model = joblib.load("embedding_model.pkl")


# -------- Annotation Normalization --------
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


# -------- Explanation Generator --------
def generate_explanation(behavior_score, text_score, final_score, threshold):

    explanation = []

    if behavior_score > 0.6:
        explanation.append("Behavioral metrics indicate elevated risk.")
    else:
        explanation.append("Behavioral signals appear moderate or low.")

    if text_score > 0.6:
        explanation.append("Annotation reasoning aligns strongly with fraud indicators.")
    else:
        explanation.append("Annotation reasoning is limited or lacks strong contextual evidence.")

    if final_score > threshold:
        explanation.append("Overall confidence exceeds approval threshold.")
    else:
        explanation.append("Overall confidence does not meet approval threshold.")

    return " ".join(explanation)


# -------- Random Case Generator --------
def generate_random_case():

    order_velocity = round(random.uniform(2, 12), 2)
    device_changes = random.randint(0, 4)
    ip_changes = random.randint(0, 3)
    unpaid_ratio = round(random.uniform(0.0, 0.8), 2)
    risky_flag = random.choice([0, 1])

    annotation_templates = [
        "order vel; card vel; multiple device changes observed.",
        "ip chg detected with elevated order velocity.",
        "high unpaid ratio with risky category purchases.",
        "order vel spike; dev chg; possible coordinated misuse.",
        "moderate activity increase but no strong cluster linkage.",
        "card vel; ip chg; prior suspicious activity noted."
    ]

    annotation = random.choice(annotation_templates)

    return {
        "order_velocity": order_velocity,
        "device_changes": device_changes,
        "ip_changes": ip_changes,
        "unpaid_ratio": unpaid_ratio,
        "risky_flag": risky_flag,
        "annotation": annotation
    }


# -------- Main Route --------
@app.route("/", methods=["GET", "POST"])
def home():

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

        # Normalize annotation
        clean_annotation = normalize_annotation(annotation)

        # Behavioral prediction
        X_behavior = np.array([[
            order_velocity,
            device_changes,
            ip_changes,
            unpaid_ratio,
            risky_flag
        ]])

        behavior_score = behavior_model.predict_proba(X_behavior)[0][1]

        # Text prediction
        embedding = embedding_model.encode([clean_annotation])
        text_score = text_model.predict_proba(embedding)[0][1]

        # Weighted final score
        final_score = 0.3 * behavior_score + 0.7 * text_score

        decision = "APPROVE" if final_score > threshold else "REJECT"

        explanation = generate_explanation(
            behavior_score,
            text_score,
            final_score,
            threshold
        )

        # Prepare next random case after evaluation
        next_case = generate_random_case()

        return render_template(
            "index.html",
            behavior_score=round(behavior_score, 3),
            text_score=round(text_score, 3),
            final_score=round(final_score, 3),
            decision=decision,
            threshold=threshold,
            explanation=explanation,
            request_id=request_id,
            timestamp=timestamp,
            case_data=next_case
        )

    # On first load → show random case
    random_case = generate_random_case()

    return render_template(
        "index.html",
        threshold=0.5,
        case_data=random_case
    )


if __name__ == "__main__":
    app.run(debug=True)
