from flask import Flask, request
from models import db, Player, Game, connect_to_db

app = Flask(__name__)

app.secret_key = "lafoijasfoaijspofjas"


# add new players
@app.route("/add_player")
def add_player():
    """Add a new player to the r00tz database."""

    username = request.form.get("username")
    team_name = request.form.get("team_name")

    if (username,) not in db.session.query(Player.username).all():
        user_record = User(username=username, team_name=team_name)
        db.session.add(user_record)
        db.session.commit()


@app.route("/record_game")
def record_game():
    """Add a new game to the r00tz database."""

    challenge = request.form.get("challenge")
    player1_id = request.form.get("player1_id")
    player1_win = request.form.get("player1_win")
    player2_id = request.form.get("player2_id")
    player2_win = request.form.get("player2_win")
    initiated_at = request.form.get("initiated_at")


    user_record = User(username=username, team_name=team_name)
    db.session.add(user_record)
    db.session.commit()


if __name__ == "__main__":
    connect_to_db(app, "r00tz27")
    db.create_all()