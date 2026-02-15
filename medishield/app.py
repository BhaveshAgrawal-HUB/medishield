from flask import Flask, render_template, redirect, url_for, session, request
import os

app = Flask(__name__)
app.secret_key = "medishield_secret_key"

@app.route("/")
def home():
    return render_template("landing.html", logged_in=session.get("user"))

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        session["user"] = True
        return redirect(url_for("home"))
    return render_template("login.html")

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        return redirect(url_for("login"))
    return render_template("register.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))

@app.route("/predict")
def predict():
    return render_template("predict.html")

@app.route("/result")
def result():
    return render_template("result.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
