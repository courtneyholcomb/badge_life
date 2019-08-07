"""Models for R00tz27 game."""

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy(app)


def connect_to_db(app, db_name):
    """Connect to database."""

    app.config["SQLALCHEMY_DATABASE_URI"] = f"postgresql:///r00tz27"
    app.config["SQLALCHEMY_ECHO"] = True
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.app = app
    db.init_app(app)


class Player(db.Model):
    """R00tz27 game player."""

    __tablename__ = "players"

    player_id = db.Column(db.Integer, autoincrement=True, primary_key=True)
    username = db.Column(db.String(255), nullable=False)
    team_name = db.Column(db.String(255), nullable=False)

    # how to add together multiple foreign keys?
    # games = db.relationship("Game")


    def __repr__(self):
        """Show info about player."""

        return f"<Player player_id={ self.player_id } username={ self.username }>"


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

    player1 = db.relationship("Player", 
                              primaryjoin='Game.player1_id == Player.player_id')
    player2 = db.relationship("Player", 
                              primaryjoin='Game.player2_id == Player.player_id')

    def __repr__(self):
        """Show game details."""

        return f"""Game game_id={ self.game_id } player1={ self.player1_id } 
                   player2={ self.player2_id }"""
