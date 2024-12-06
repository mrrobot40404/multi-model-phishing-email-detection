from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

def analyze_email(email):
    # Replace with the actual email analysis logic
    return f"Analysis complete for: {email}. No phishing detected."

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    email = data.get("email")
    if not email or not email.strip():
        return jsonify({"result": "Please enter an email."})
    result = analyze_email(email)
    return jsonify({"result": result})

if __name__ == "__main__":
    app.run(debug=True)
