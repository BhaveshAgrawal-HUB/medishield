from flask import Flask, render_template, redirect, url_for, session, request
import joblib
import pandas as pd
import json
import os
import difflib

app = Flask(__name__)
app.secret_key = "medishield_secret_key"

# ===== LOAD MODEL =====
model = joblib.load("model.pkl")
le_drug = joblib.load("le_drug.pkl")
le_side = joblib.load("le_side.pkl")

# ===== LOAD DATASET =====
df = pd.read_csv("medicine_dataset.csv", low_memory=False)
df.columns = df.columns.str.strip()
drug_list = sorted(df["name"].dropna().str.lower().str.strip().unique())

# ===== USER FILE =====
USER_FILE = "users.json"

if not os.path.exists(USER_FILE):
    with open(USER_FILE, "w") as f:
        json.dump({}, f)

def load_users():
    with open(USER_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USER_FILE, "w") as f:
        json.dump(users, f, indent=4)

# ===== USER HISTORY =====
user_history = {}

# ===== NORMALIZE DRUG =====
def normalize_drug_name(user_input):
    user_input = user_input.lower().strip()

    if user_input in drug_list:
        return user_input

    match = difflib.get_close_matches(user_input, drug_list, n=1, cutoff=0.6)
    return match[0] if match else None


# ================= ROUTES =================

@app.route("/")
def home():
    return render_template("landing.html", logged_in=session.get("user"))


# ===== REGISTER =====
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        fname = request.form.get("fname")
        lname = request.form.get("lname")
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        if email in users:
            return "User already exists!"

        users[email] = {
            "fname": fname,
            "lname": lname,
            "password": password
        }

        save_users(users)

        return redirect(url_for("login"))

    return render_template("register.html")


# ===== LOGIN =====
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")
        password = request.form.get("password")

        users = load_users()

        if email in users and users[email]["password"] == password:
            session["user"] = email
            return redirect(url_for("home"))
        else:
            return "Invalid email or password!"

    return render_template("login.html")


# ===== LOGOUT =====
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


# ===== PROFILE =====
@app.route("/profile")
def profile():
    if not session.get("user"):
        return redirect(url_for("login"))

    user = session.get("user")
    users = load_users()
    history = user_history.get(user, [])

    return render_template(
        "dashboard.html",
        history=history,
        user=users[user]["fname"]
    )


# ===== PREDICT =====
@app.route("/predict", methods=["GET", "POST"])
def predict():

    if not session.get("user"):
        return redirect(url_for("login"))

    if request.method == "POST":

        age = request.form.get("age")
        gender = request.form.get("gender")
        conditions = request.form.get("conditions")
        drug_input = request.form.get("drug")

        drug = normalize_drug_name(drug_input)

        if drug is None:
            results = [("Invalid medicine name", 0)]
        else:
            try:
                drug_encoded = le_drug.transform([drug])[0]

                probs = model.predict_proba([[drug_encoded]])[0]
                top_indices = probs.argsort()[-3:][::-1]

                results = []
                for i in top_indices:
                    effect = le_side.inverse_transform([i])[0]
                    confidence = round(probs[i] * 100, 2)
                    results.append((effect, confidence))

            except:
                results = [("Invalid medicine name", 0)]

        # SAVE HISTORY
        user = session.get("user")

        if user not in user_history:
            user_history[user] = []

        user_history[user].append({
            "drug": drug_input,
            "results": results
        })

        return render_template(
            "result.html",
            results=results,
            age=age,
            gender=gender,
            conditions=conditions if conditions else "None"
        )

    return render_template("predict.html", drugs=drug_list)


if __name__ == "__main__":
    app.run(debug=True)
