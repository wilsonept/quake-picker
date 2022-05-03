import random
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField
from wtforms.validators import DataRequired, AnyOf

from models import Game_mode, Bo_type, Rule

"""
Файл с формами приложения.
    - `CreateForm`: форма создания игры.
    - `JoinForm`: форма подключения к игре.

"""


# ------ Формы ---------------------------------------------------------

class CreateForm(FlaskForm):
    """Форма создания игры."""
    game_modes = ["duel"]
    game_mode = SelectField(label=u"Game Mode", choices=game_modes,
                           validators=[DataRequired(), AnyOf(game_modes)])
    bo_types = ["bo3"]
    bo_type = SelectField(label=u"Game Mode", choices=bo_types,
                         validators=[DataRequired(), AnyOf(bo_types)])
    nickname = StringField(label=u"Nickname",
                           validators=[DataRequired()])
    seeds = ["Random", "You", "Opponent"]
    seed = SelectField(label=u"Seed", choices=seeds,
                       validators=[DataRequired(), AnyOf(seeds)])
    submit = SubmitField(label="Submit")

    
class JoinForm(FlaskForm):
    """Форма подключения к игре."""
    nickname = StringField(label=u"Nickname", validators=[DataRequired()])
    submit = SubmitField(label="Submit")
