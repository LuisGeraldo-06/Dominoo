from flask import Flask, render_template_string, request, redirect
import random

app = Flask(__name__)

THEMES=[
("#ffd6e0","Poppins"),("#d6f5ff","Nunito"),("#e7ffd6","Quicksand"),
("#f7d6ff","Comfortaa"),("#fff0c9","Raleway"),("#ffdacf","Montserrat"),
("#d9d6ff","Ubuntu"),("#d6ffe9","Lato"),("#ffe6f2","Merriweather"),
("#e6fff9","Rubik"),("#f2ffd6","Inter"),("#ffd6f5","Karla"),
("#d6e4ff","Josefin Sans"),("#ffe0d6","Open Sans"),("#e0ffd6","Source Sans Pro")
]

def random_theme():
color,font=random.choice(THEMES)
return {"color":color,"font":font}

class GameState:
def __init__(self):
self.reset()

def reset(self):
self.teamA=""
self.teamB=""
self.goal=100
self.rounds=[]
self.theme=random_theme()
self.dark=True
self.configured=False
self.error=None

def totals(self):
return sum(r[0] for r in self.rounds),sum(r[1] for r in self.rounds)

game=GameState()

HTML="""
<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<link href="https://fonts.googleapis.com/css2?family={{theme.font.replace(' ','+')}}&display=swap" rel="stylesheet">

<style>
body{
margin:0;
font-family:'{{theme.font}}',sans-serif;
background:{{'#111' if dark else 'white'}};
color:{{'white' if dark else '#333'}};
}

.container{max-width:720px;margin:auto;padding:20px;}

.card{
background:{{'#1e1e1e' if dark else 'white'}};
padding:25px;border-radius:20px;
box-shadow:0 10px 25px rgba(0,0,0,.15);
}

h1{text-align:center}

input,button,select{
padding:14px;margin:6px 0;width:100%;
border:none;border-radius:12px;font-size:16px;
}

button{background:{{theme.color}};font-weight:bold;cursor:pointer}

table{width:100%;margin-top:15px;border-collapse:collapse}
td,th{padding:12px;text-align:center}

.divider{width:4px;background:{{theme.color}}}

.teamTitle{font-size:22px;font-weight:900}
.subtitle{font-size:12px;opacity:.6}

.overlay{
position:fixed;top:0;left:0;width:100%;height:100%;
background:black;color:white;
display:flex;flex-direction:column;
justify-content:center;align-items:center;
font-size:42px;
}

.error{
background:#ff4d6d;
padding:12px;
border-radius:12px;
margin-bottom:10px;
text-align:center;
font-weight:bold;
}

.totalBox{
display:flex;
justify-content:space-between;
font-size:20px;
font-weight:bold;
margin-top:15px;
}
</style>

<script>
function toggleDark(){fetch("/dark").then(()=>location.reload())}
function changeTheme(){fetch("/theme").then(()=>location.reload())}
</script>
</head>

<body>

{% if winner %}
<div class="overlay">
<div>🏆 {{winner}} GANÓ 🏆</div>
<form method="POST" action="/reset">
<button style="width:auto;margin-top:25px;">Nueva partida</button>
</form>
</div>
{% endif %}

<div class="container">
<div class="card">

<h1>DOMINICAN DOMINO's</h1>

{% if error %}
<div class="error">{{error}}</div>
{% endif %}

<button onclick="toggleDark()">Modo {{ "Claro" if dark else "Oscuro" }}</button>
<button onclick="changeTheme()">Cambiar tema</button>

{% if not configured %}
<form method="POST" action="/setup">
<input name="teamA" placeholder="Equipo A" required>
<input name="teamB" placeholder="Equipo B" required>
<input name="goal" type="number" placeholder="Meta puntos" required>
<label><input type="checkbox" required> Confirmar datos</label>
<button>Iniciar partida</button>
</form>
{% endif %}

{% if configured %}

<form method="POST" action="/add">
<input name="a" type="number" placeholder="Puntos {{teamA}}">
<input name="b" type="number" placeholder="Puntos {{teamB}}">
<button>Agregar ronda</button>
</form>

<table>
<tr>
<th>Ronda</th>

<th>
<div class="teamTitle">{{teamA}}</div>
<div class="subtitle">Equipo</div>
<form method="POST" action="/bonus/A">
<select name="type">
<option>SALIDA</option>
<option>PASE CORRIDO</option>
<option>CAPI-CUA</option>
</select>
<button>Agregar</button>
</form>
</th>

<td class="divider"></td>

<th>
<div class="teamTitle">{{teamB}}</div>
<div class="subtitle">Equipo</div>
<form method="POST" action="/bonus/B">
<select name="type">
<option>SALIDA</option>
<option>PASE CORRIDO</option>
<option>CAPI-CUA</option>
</select>
<button>Agregar</button>
</form>
</th>
</tr>

{% for r in rounds %}
<tr>
<td>{{loop.index}}</td>

<td>
<form method="POST" action="/edit/{{loop.index0}}">
<input name="a" type="number" value="{{r[0]}}">
<input type="hidden" name="b" value="{{r[1]}}">
<button>✓</button>
</form>
</td>

<td class="divider"></td>

<td>
<form method="POST" action="/edit/{{loop.index0}}">
<input name="b" type="number" value="{{r[1]}}">
<input type="hidden" name="a" value="{{r[0]}}">
<button>✓</button>
</form>
</td>
</tr>
{% endfor %}
</table>

<div class="totalBox">
<div>{{teamA}}: {{totalA}}</div>
<div>{{teamB}}: {{totalB}}</div>
</div>

<form method="POST" action="/reset">
<button style="background:#ff6b6b">Reset partida</button>
</form>

{% endif %}
</div>
</div>
</body>
</html>
"""

@app.route("/")
def home():
winner=None
totalA,totalB=game.totals()

if game.configured:
if totalA>=game.goal: winner=game.teamA
elif totalB>=game.goal: winner=game.teamB

return render_template_string(HTML,**game.__dict__,winner=winner,totalA=totalA,totalB=totalB)

@app.route("/setup",methods=["POST"])
def setup():
game.teamA=request.form["teamA"]
game.teamB=request.form["teamB"]
game.goal=int(request.form["goal"])
game.configured=True
return redirect("/")

@app.route("/add",methods=["POST"])
def add():
a=int(request.form.get("a") or 0)
b=int(request.form.get("b") or 0)
game.rounds.append([a,b])
return redirect("/")

@app.route("/edit/<int:i>",methods=["POST"])
def edit(i):
a=int(request.form.get("a") or 0)
b=int(request.form.get("b") or 0)
game.rounds[i]=[a,b]
return redirect("/")

@app.route("/bonus/<team>",methods=["POST"])
def bonus(team):

if not game.rounds:
game.rounds.append([0,0])

totalA,totalB=game.totals()

if team=="A":
if totalA+30>=game.goal:
game.error="NO SE PUEDEN INGRESAR EL VALOR."
return redirect("/")
game.rounds[-1][0]+=30
else:
if totalB+30>=game.goal:
game.error="NO SE PUEDEN INGRESAR EL VALOR."
return redirect("/")
game.rounds[-1][1]+=30

game.error=None
return redirect("/")

@app.route("/reset",methods=["POST"])
def reset():
game.reset()
return redirect("/")

@app.route("/dark")
def dark():
game.dark=not game.dark
return ("",204)

@app.route("/theme")
def theme():
game.theme=random_theme()
return ("",204)

if __name__ == "__main__":
  app.run()
