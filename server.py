import os

from flask import Flask, request, render_template, flash, redirect
from flask_debugtoolbar import DebugToolbarExtension
from flask_sqlalchemy import SQLAlchemy

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
    name = db.Column(db.String(255), nullable=False)
    mac = db.Column(db.String(255), nullable=False, unique=True)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.id"), nullable=False)

    # games = # TODO

    def __repr__(self):
        """Show info about player."""
        return f"<Player id={ self.id } name={ self.name }>"


class Game(db.Model):
    """R00tz27 game."""

    __tablename__ = "games"
    __table_args__ = (
        db.UniqueConstraint(
            "challenge", "player1_id", "player2_id", name="unique_players_challenge"
        ),
    )

    id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    challenge = db.Column(db.Integer, nullable=False)

    player1_id = db.Column(db.Integer, db.ForeignKey("players.id"))
    player1_win = db.Column(db.Boolean)
    player2_id = db.Column(db.Integer, db.ForeignKey("players.id"))
    player2_win = db.Column(db.Boolean)

    played_at = db.Column(db.DateTime)

    def __repr__(self):
        """Show game details."""
        return f"<Game id={ self.id } player1={ self.player1_id } player2={ self.player2_id }>"


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


@app.route("/")
def show_homepage():
    """Show homepage."""
    return render_template("homepage.html")


@app.route("/register", methods=["GET"])
def show_registration_page():
    """Show form to register new player."""
    return render_template("register.html", teams=Team.query.all())


@app.route("/register", methods=["POST"])
def add_player():
    """Add a new player to the r00tz database."""

    username = request.form.get("username")
    team_id = int(request.form.get("team_id"))

    if (username,) not in db.session.query(Player.username).all():
        player_record = Player(username=username, team_id=team_id)
        db.session.add(player_record)
        db.session.commit()

        flash(f"New player added successfully! Username: {username}")

    else:
        flash("That username is already taken. Please choose another.")

    return redirect("/register")


@app.route("/record_game", methods=["POST"])
def record_game():
    """Add a new game to the r00tz database."""

    # challenge = request.form.get("challenge")
    # player1_id = request.form.get("player1_id")
    # player1_win = request.form.get("player1_win")
    # player2_id = request.form.get("player2_id")
    # player2_win = request.form.get("player2_win")
    # initiated_at = request.form.get("initiated_at")

    # add game to games table
    game_record = Game(
        challenge=challenge,
        player1_id=player1_id,
        player1_win=player1_win,
        player2_id=player2_id,
        player2_win=player2_win,
        initiated_at=initiated_at,
    )

    # add games to players' games_played
    player1 = Player.query.get(player1_id)
    player2 = Player.query.get(player2_id)

    # write columns explicitly (instead of += 1) to avoid race conditions
    player1.games_played = player1.games_played + 1
    player2.games_played = player2.games_played + 1

    # increment games won for winners
    if player1_win:
        player1.games_won = player1.games_won + 1
    if player2_win:
        player2.games_won = player2.games_won + 1

    # if opposing teams, increment teams' games_played & games_won
    if player1.team != player2.team:

        player1.team.games_played = player1.team.games_played + 1
        player2.team.games_played = player2.team.games_played + 1

        if player1_win:
            player1.team.games_won = player1.team.games_won + 1

        if player2_win:
            player2.team.games_won = player2.team.games_won + 1

    db.session.add(game_record)
    db.session.commit()

    # add records to game_players table
    gp_record1 = GamePlayer(game_id=game_record.game_id, player_id=player1_id)
    gp_record2 = GamePlayer(game_id=game_record.game_id, player_id=player2_id)

    db.session.add(gp_record1)
    db.session.add(gp_record2)
    db.session.commit()


@app.route("/leaderboard", methods=["GET"])
def show_leaderboard():
    """Show team and player rankings."""

    players = Player.query.order_by(Player.games_won.desc()).all()
    teams = Team.query.order_by(Team.games_won.desc()).all()

    return render_template("leaderboard.html", players=players, teams=teams)


if __name__ == "__main__":
    db.create_all()
    seed_teams()

    app.debug = True
    app.jinja_env.auto_reload = app.debug
    DebugToolbarExtension(app)

    app.run(port=5000, host="0.0.0.0")
