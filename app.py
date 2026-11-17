from flask import Flask, render_template, request, jsonify
from agent import run_agent


app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/chat", methods=["POST"])
def chat():

    data = request.get_json(silent=True) or {}

    user_message = data.get("message", "")

    print("USER REQUEST RECEIVED:", user_message)

    result = run_agent(user_message)

    print("AGENT RESULT:", result)

    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True, port=5000)