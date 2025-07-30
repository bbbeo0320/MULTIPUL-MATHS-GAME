from flask import Flask, render_template, request, redirect, url_for, jsonify
import json
import os

app = Flask(__name__)

# Load or initialize leaderboard
if os.path.exists("leaderboard.json"):
    with open("leaderboard.json") as f:
        leaderboard = json.load(f)
else:
    leaderboard = []

@app.route('/')
def home():
    return render_template('home.html', leaderboard=leaderboard)

@app.route('/play')
def play():
    return render_template('play.html')

@app.route('/submit', methods=['POST'])# Remove this line:

def submit():
    name = request.form.get("name")
    score = int(request.form.get("score", 0))
    leaderboard.append({"name": name, "score": score})
    leaderboard.sort(key=lambda x: x["score"], reverse=True)
    leaderboard[:] = leaderboard[:5]  # keep top 5
    with open("leaderboard.json", "w") as f:
        json.dump(leaderboard, f)
    return redirect(url_for("home"))

if __name__ == '__main__':
    app.run(debug=True)
