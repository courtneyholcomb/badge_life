import os

from flask import Flask, request, render_template, flash, redirect
from models import db, Player, Game, Team, GamePlayer, connect_to_db
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)

app.secret_key = os.environ.get("SECRET_KEY", "trustno1")


def seed_teams():
    """Create teams."""
    team_names = [team.name for team in Team.query.all()]

    if "tiger" not in team_names:
        team1 = Team(team_id=1, name="tiger")
        db.session.add(team1)

    if "wolf" not in team_names:
        team2 = Team(team_id=2, name="wolf")
        db.session.add(team2)

    db.session.commit()


@app.route("/")
def show_homepage():
    """Show homepage."""

    return render_template("homepage.html")


@app.route("/register", methods=["GET"])
def show_registration_page():
    """Show form to register new player."""

    usernames = [player.username for player in Player.query.all()]

    return render_template("register.html", usernames=usernames)


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
    connect_to_db(app, "r00tz27")
    db.create_all()
    seed_teams()

    app.debug = True
    app.jinja_env.auto_reload = app.debug
    DebugToolbarExtension(app)

    app.run(port=5000, host="0.0.0.0")

