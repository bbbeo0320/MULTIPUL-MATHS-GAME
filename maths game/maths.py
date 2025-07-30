from flask import Flask, render_template_string, request, redirect, url_for, session
import random, json, os

app = Flask(__name__)
app.secret_key = 'supersecretkey'

SAVE_FILE = "leaderboard.json"

if os.path.exists(SAVE_FILE):
    with open(SAVE_FILE) as f:
        leaderboard = json.load(f)
else:
    leaderboard = []

TEMPLATE = """
<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>📚 Math Challenge 🎲</title>
<style>
body { font-family: Arial, sans-serif; text-align: center; background: #f9f9f9; }
h1 { color: #444; }
button, input[type=submit] {
  padding: 10px 20px; font-size: 1em; margin: 10px; cursor: pointer; border-radius:5px;
}
form { margin-top: 20px; }
</style>
</head>
<body>

<h1>📚 Math Challenge 🎲</h1>

{% if not session.get('name') %}
<form method="post" action="/set_name">
  <input name="name" placeholder="Enter your name" required>
  <input type="submit" value="Start">
</form>

{% elif not question %}
<form method="post" action="/start">
  <input type="submit" value="▶ Start Game">
</form>

<form method="get" action="/leaderboard">
  <input type="submit" value="🏆 Leaderboard">
</form>

{% else %}
<div>
  <p><b>{{ session.name }}</b> | Coins: {{ session.coins }}</p>
  <p>⏳ Time left: {{ session.time_left }}s</p>
  <p><b>{{ question }}</b></p>
  <form method="post" action="/answer">
    <input name="answer" placeholder="Your answer" autofocus required>
    <input type="submit" value="Submit">
  </form>
  {% if msg %}<p>{{ msg }}</p>{% endif %}
</div>
{% endif %}

{% if leaderboard %}
<div style="margin-top:50px">
  <h2>🏆 Leaderboard</h2>
  <ol>
  {% for entry in leaderboard %}
    <li>{{ entry.name }} — {{ entry.coins }} coins</li>
  {% endfor %}
  </ol>
</div>
{% endif %}

</body>
</html>
"""

def generate_problem():
    n1, n2 = random.randint(1,20), random.randint(1,20)
    op = random.choice(['+', '-', '*'])
    if op == '+': ans = n1 + n2
    elif op == '-': ans = n1 - n2
    else: ans = n1 * n2
    return f"{n1} {op} {n2} = ?", ans

@app.route("/", methods=["GET"])
def home():
    q = session.get("question")
    return render_template_string(TEMPLATE,
                                  question=q,
                                  msg=session.pop("msg", ""),
                                  leaderboard=leaderboard)

@app.route("/set_name", methods=["POST"])
def set_name():
    session["name"] = request.form["name"]
    session["coins"] = 0
    session["time_left"] = 60
    session["question"] = None
    return redirect(url_for("home"))

@app.route("/start", methods=["POST"])
def start():
    q,a = generate_problem()
    session["question"] = q
    session["answer"] = a
    session["time_left"] = 60
    return redirect(url_for("home"))

@app.route("/answer", methods=["POST"])
def answer():
    if session.get("time_left",0)<=0:
        session["msg"] = "⏳ Time’s up!"
        session["question"] = None
        return redirect(url_for("home"))

    try:
        ans = int(request.form["answer"])
        if ans == session["answer"]:
            session["coins"] += 10
            session["msg"] = "✅ Correct! +10 coins"
        else:
            session["msg"] = f"❌ Wrong! Correct was {session['answer']}"
    except:
        session["msg"] = "⚠ Invalid input"
    session["time_left"] -= 5

    if session["time_left"] <= 0:
        leaderboard.append({"name":session["name"],"coins":session["coins"]})
        leaderboard.sort(key=lambda x:x["coins"],reverse=True)
        leaderboard[:] = leaderboard[:5]
        with open(SAVE_FILE,"w") as f:
            json.dump(leaderboard,f,indent=2)
        session["msg"] += " | 🎮 Game over!"
        session["question"] = None
    else:
        q,a = generate_problem()
        session["question"] = q
        session["answer"] = a

    return redirect(url_for("home"))

@app.route("/leaderboard", methods=["GET"])
def lb():
    return render_template_string(TEMPLATE,
                                  question=None,
                                  msg=None,
                                  leaderboard=leaderboard)

if __name__ == "__main__":
    app.run(debug=True)
