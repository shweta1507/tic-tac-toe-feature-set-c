from flask import Flask, jsonify, render_template, request, session
import random

app = Flask(__name__)
app.secret_key = "college-tic-tac-toe-key"

WINNING_LINES = [(0,1,2),(3,4,5),(6,7,8),(0,3,6),(1,4,7),(2,5,8),(0,4,8),(2,4,6)]

def winner(board):
    for a,b,c in WINNING_LINES:
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    return None

def full(board): return all(x is not None for x in board)
def result(board):
    w = winner(board)
    return w or ("Draw" if full(board) else None)
def empty(board): return [i for i,x in enumerate(board) if x is None]

def winning_move(board, player):
    for i in empty(board):
        b=board.copy(); b[i]=player
        if winner(b)==player: return i
    return None

def minimax(board, maximizing):
    r=result(board)
    if r=="O": return 10
    if r=="X": return -10
    if r=="Draw": return 0
    if maximizing:
        best=-float("inf")
        for i in empty(board):
            b=board.copy(); b[i]="O"
            best=max(best,minimax(b,False))
        return best
    best=float("inf")
    for i in empty(board):
        b=board.copy(); b[i]="X"
        best=min(best,minimax(b,True))
    return best

def computer_move(board, difficulty):
    cells=empty(board)
    if not cells: return None
    if difficulty=="Easy": return random.choice(cells)
    if difficulty=="Medium":
        i=winning_move(board,"O")
        if i is not None: return i
        i=winning_move(board,"X")
        return i if i is not None else random.choice(cells)
    best=-float("inf"); move=cells[0]
    for i in cells:
        b=board.copy(); b[i]="O"
        score=minimax(b,False)
        if score>best: best,move=score,i
    return move

def init_session():
    session.setdefault("scores",{"wins":0,"losses":0,"draws":0})
    session.setdefault("history",[])

@app.route("/")
def home():
    init_session()
    return render_template("index.html")

@app.post("/api/computer-move")
def api_move():
    data=request.get_json(silent=True) or {}
    board=data.get("board"); difficulty=data.get("difficulty","Medium")
    if not isinstance(board,list) or len(board)!=9 or any(x not in (None,"X","O") for x in board):
        return jsonify(error="Invalid board"),400
    if difficulty not in ("Easy","Medium","Hard"): return jsonify(error="Invalid difficulty"),400
    if result(board): return jsonify(board=board,move=None,result=result(board))
    i=computer_move(board,difficulty)
    b=board.copy(); b[i]="O"
    return jsonify(board=b,move=i,result=result(b))

@app.post("/api/result")
def api_result():
    data=request.get_json(silent=True) or {}
    r=data.get("result"); d=data.get("difficulty","Medium")
    if r not in ("X","O","Draw"): return jsonify(error="Invalid result"),400
    init_session()
    scores=session["scores"].copy()
    scores[{"X":"wins","O":"losses","Draw":"draws"}[r]] += 1
    history=list(session["history"])
    history.insert(0,{"winner":r,"difficulty":d})
    session["scores"]=scores; session["history"]=history[:30]
    return jsonify(scores=scores,history=session["history"])

@app.get("/api/state")
def state():
    init_session()
    return jsonify(scores=session["scores"],history=session["history"])

@app.post("/api/reset")
def reset():
    session["scores"]={"wins":0,"losses":0,"draws":0}
    session["history"]=[]
    return jsonify(scores=session["scores"],history=[])

if __name__=="__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
