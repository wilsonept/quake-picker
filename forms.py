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

    def convert_data(self, game_mode, bo_type, seed, nickname) -> dict:
        """
        Конвертирует полученные строчные данные в id'шники
        Принимает на вход строковые значения:
            - `game_mode`
            - `bo_type`
            - `seed`

        Возвращает словарь:
            - `game_mode_id`
            - `bo_type_id`
            - `seed`
        """

        game_mode_id = Game_mode.query.filter_by(name=game_mode).first().id
        bo_type_id = Bo_type.query.filter_by(name=bo_type).first().id

        # Находим первый шаг в правилах по выбранным game_mode и bo_type.
        clause = {
            "game_mode_id": game_mode_id,
            "bo_type_id": bo_type_id,
            "step": 1
        }
        current_step_id = Rule.query.filter_by(**clause).first().id

        # Присваиваем значение seed на основе выбора пользователя.
        if seed == "Opponent":
            seed = 2
        elif seed == "You":
            seed = 1
        else:
            seed = random.choice([1, 2])

        return  {
            "nickname": nickname,
            'seed': seed,
            'current_step_id': current_step_id
        }
    
class JoinForm(FlaskForm):
    """Форма подключения к игре."""
    nickname = StringField(label=u"Nickname", validators=[DataRequired()])
    submit = SubmitField(label="Submit")
