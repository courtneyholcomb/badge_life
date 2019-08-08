"""Models for R00tz27 game."""

import os
from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def connect_to_db(app, db_name):
    """Connect to database."""

    app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get(
        "DATABASE_URL", "postgresql:///r00tz27"
    )
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = app
    db.init_app(app)


class Player(db.Model):
    """R00tz27 game player."""

    __tablename__ = "players"

    player_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    team_id = db.Column(db.Integer, db.ForeignKey("teams.team_id"))
    games_played = db.Column(db.Integer, default=0, nullable=False)
    games_won = db.Column(db.Integer, default=0, nullable=False)

    team = db.relationship("Team", backref="players", uselist=False)
    games = db.relationship("Game", secondary="game_players", backref="players")

    def __repr__(self):
        """Show info about player."""

        return f"<Player player_id={ self.player_id } " f"username={ self.username }>"


class Game(db.Model):
    """R00tz27 game."""

    __tablename__ = "games"

    game_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    challenge = db.Column(db.Integer, nullable=False)
    player1_id = db.Column(db.Integer, db.ForeignKey("players.player_id"))
    player1_win = db.Column(db.Boolean)
    player2_id = db.Column(db.Integer, db.ForeignKey("players.player_id"))
    player2_win = db.Column(db.Boolean)
    initiated_at = db.Column(db.DateTime)

    player1 = db.relationship(
        "Player", primaryjoin="Game.player1_id == Player.player_id"
    )
    player2 = db.relationship(
        "Player", primaryjoin="Game.player2_id == Player.player_id"
    )

    def __repr__(self):
        """Show game details."""

        return (
            f"<Game game_id={ self.game_id } player1={ self.player1_id } "
            f"player2={ self.player2_id }>"
        )


class Team(db.Model):
    """Team in the r00tz27 game."""

    __tablename__ = "teams"

    team_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    name = db.Column(db.String(255), nullable=False)
    games_played = db.Column(db.Integer, default=0, nullable=False)
    games_won = db.Column(db.Integer, default=0, nullable=False)

    def __repr__(self):
        """Show team name."""

        return f"""<Team name={self.name}>"""


class GamePlayer(db.Model):
    """Association between games and players."""

    __tablename__ = "game_players"

    gameplayer_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey("games.game_id"))
    player_id = db.Column(db.Integer, db.ForeignKey("players.player_id"))

    game = db.relationship("Game", uselist=False, backref="game_player_objects")
    player = db.relationship("Player", uselist=False, backref="game_player_objects")

