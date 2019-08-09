import json
import os

from flask import Flask, flash, redirect, render_template, request, jsonify
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "trustno1")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
    "DATABASE_URL", "postgresql:///r00tz27"
)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
db.app = app
db.init_app(app)


class Team(db.Model):
    """Team in the r00tz27 game."""

    __tablename__ = "teams"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    name_plural = db.Column(db.String(255), nullable=False)

    players = db.relationship("Player", backref="team")

    def __repr__(self):
        """Show team name."""
        return f"<Team name={self.name}>"


class Player(db.Model):
    """R00tz27 game player."""

    __tablename__ = "players"

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False, unique=True)
    mac = db.Column(db.String(255), nullable=False, unique=True)
    team_name = db.Column(db.String(255), db.ForeignKey("teams.name"), nullable=False)

    player1 = db.relationship(
        "Game", backref="games_as_p1", foreign_keys="Game.player1_mac"
    )
    player2 = db.relationship(
        "Game", backref="games_as_p2", foreign_keys="Game.player2_mac"
    )

    def __repr__(self):
        """Show info about player."""
        return f"<Player id={ self.id } name={ self.name }>"


class Game(db.Model):
    """R00tz27 game."""

    __tablename__ = "games"
    __table_args__ = (
        db.UniqueConstraint(
            "challenge", "player1_mac", "player2_mac", name="unique_players_challenge"
        ),
    )

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    challenge = db.Column(db.Integer, nullable=False)

    player1_mac = db.Column(db.String(255), db.ForeignKey("players.mac"))
    player1_win = db.Column(db.Boolean)
    player2_mac = db.Column(db.String(255), db.ForeignKey("players.mac"))
    player2_win = db.Column(db.Boolean)

    # played_at = db.Column(db.DateTime)

    def __repr__(self):
        """Show game details."""
        return f"<Game id={ self.id } player1={ self.player1_mac } player2={ self.player2_mac }>"


def seed_teams():
    """Create teams."""
    team_names = [team.name for team in Team.query.all()]

    if "tiger" not in team_names:
        team1 = Team(id=0, name="tiger", name_plural="tigers")
        db.session.add(team1)

    if "wolf" not in team_names:
        team2 = Team(id=1, name="wolf", name_plural="wolves")
        db.session.add(team2)

    db.session.commit()


@app.route("/register", methods=["POST"])
def add_player():
    """Add a new player to the r00tz database."""
    try:
        player = json.loads(request.values["json"])

        name = player["name"]
        mac = player["mac"]
        team_name = player["team_name"]
    except json.decoder.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400
    except KeyError:
        return jsonify({"error": "Missing required field"}), 400

    if Player.query.filter(or_(Player.name == name, Player.mac == mac)).count() > 0:
        return jsonify({"error": "Player name & mac must be unique"}), 400

    try:
        player_record = Player(name=name, mac=mac, team_name=team_name)
        db.session.add(player_record)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as err:
        return jsonify({"error": str(err)}), 400


@app.route("/record_games", methods=["POST"])
def record_games():
    """Add new games to the r00tz database."""
    try:
        games = json.loads(request.values["json"])
    except json.decoder.JSONDecodeError:
        return jsonify({"error": "Invalid JSON"}), 400

    for game in games:
        try:
            game_record = Game(
                challenge=game["challenge"],
                player1_mac=game["my_mac"],
                player1_win=game["i_won"],
                player2_mac=game["opponent_mac"],
                player2_win=game["they_won"],
            )

            # ensure consistent ordering of player1 and player2
            if not game_record.player1_mac > game_record.player2_mac:
                # swap the two
                game_record.player1_mac, game_record.player2_mac = (
                    game_record.player2_mac,
                    game_record.player1_mac,
                )
                game_record.player1_win, game_record.player2_win = (
                    game_record.player2_win,
                    game_record.player1_win,
                )

            db.session.add(game_record)
            db.session.commit()
        except Exception as err:
            print(err)  # that's all. don't fail uploading everything.
    return jsonify({"success": True})


@app.route("/", methods=["GET"])
def show_leaderboard():
    """Show team and player rankings."""

    players = Player.query.all()
    teams = Team.query.all()
    games = Game.query.all()

    return render_template(
        "leaderboard.html", players=players, teams=teams, games=games
    )


if __name__ == "__main__":
    db.create_all()
    seed_teams()

    app.debug = True
    app.jinja_env.auto_reload = app.debug
    DebugToolbarExtension(app)

    app.run(port=5000, host="0.0.0.0")
