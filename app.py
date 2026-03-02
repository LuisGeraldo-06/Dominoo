from flask import Flask, render_template_string, request, redirect
import random

app = Flask(__name__)

THEMES = [
("#ffd6e0","Poppins"),("#d6f5ff","Nunito"),("#e7ffd6","Quicksand"),
("#f7d6ff","Comfortaa"),("#fff0c9","Raleway"),("#ffdacf","Montserrat"),
("#d9d6ff","Ubuntu"),("#d6ffe9","Lato"),("#ffe6f2","Merriweather"),
("#e6fff9","Rubik"),("#f2ffd6","Inter"),("#ffd6f5","Karla"),
("#d6e4ff","Josefin Sans"),("#ffe0d6","Open Sans"),("#e0ffd6","Source Sans Pro")
]

def random_theme():
    color, font = random.choice(THEMES)
    return {"color": color, "font": font}


class GameState:
    def __init__(self):
        self.reset()

    def reset(self):
        self.teamA = ""
        self.teamB = ""
        self.goal = 100
        self.rounds = []
        self.theme = random_theme()
        self.dark = True
        self.configured = False
        self.error = None

    def totals(self):
        return sum(r[0] for r in self.rounds), sum(r[1] for r in self.rounds)


game = GameState()


HTML = """[PEGA AQUÍ TU HTML EXACTO SIN CAMBIOS]"""
# ↑ No lo repito para no hacer el mensaje gigante
# usa el mismo HTML que ya enviaste


@app.route("/")
def home():
    winner = None
    totalA, totalB = game.totals()

    if game.configured:
        if totalA >= game.goal:
            winner = game.teamA
        elif totalB >= game.goal:
            winner = game.teamB

    return render_template_string(
        HTML,
        **game.__dict__,
        winner=winner,
        totalA=totalA,
        totalB=totalB
    )


@app.route("/setup", methods=["POST"])
def setup():
    game.teamA = request.form["teamA"]
    game.teamB = request.form["teamB"]
    game.goal = int(request.form["goal"])
    game.configured = True
    return redirect("/")


@app.route("/add", methods=["POST"])
def add():
    a = int(request.form.get("a") or 0)
    b = int(request.form.get("b") or 0)
    game.rounds.append([a, b])
    return redirect("/")


@app.route("/edit/<int:i>", methods=["POST"])
def edit(i):
    a = int(request.form.get("a") or 0)
    b = int(request.form.get("b") or 0)
    game.rounds[i] = [a, b]
    return redirect("/")


@app.route("/bonus/<team>", methods=["POST"])
def bonus(team):

    if not game.rounds:
        game.rounds.append([0, 0])

    totalA, totalB = game.totals()

    if team == "A":
        if totalA + 30 >= game.goal:
            game.error = "NO SE PUEDEN INGRESAR EL VALOR."
            return redirect("/")
        game.rounds[-1][0] += 30
    else:
        if totalB + 30 >= game.goal:
            game.error = "NO SE PUEDEN INGRESAR EL VALOR."
            return redirect("/")
        game.rounds[-1][1] += 30

    game.error = None
    return redirect("/")


@app.route("/reset", methods=["POST"])
def reset():
    game.reset()
    return redirect("/")


@app.route("/dark")
def dark():
    game.dark = not game.dark
    return ("", 204)


@app.route("/theme")
def theme():
    game.theme = random_theme()
    return ("", 204)


if __name__ == "__main__":
    app.run()
