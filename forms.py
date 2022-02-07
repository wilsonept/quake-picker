import random
from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, AnyOf

from database import Game_mode, Bo_type, Room




# ------ Формы ----------------------------------------------------------------

class CreateForm(FlaskForm):
    game_modes = ["duel", "tdm"]
    game_mode = SelectField(label=u"Game Mode", choices=game_modes,
                            validators=[DataRequired(), AnyOf(game_modes)])
    bo_types = ["bo3", "bo1", "bo5", "bo7"]
    bo_type = SelectField(label=u"Game Mode", choices=bo_types,
                          validators=[DataRequired(), AnyOf(bo_types)])
    nickname = StringField(label=u"Nickname",
                           validators=[DataRequired()])
    seeds = ["Random", "You", "Opponent"]
    seed = SelectField(label=u"Seed", choices=seeds,
                       validators=[DataRequired(), AnyOf(seeds)])
    submit = SubmitField(label="Submit")

    # TODO Попробовать реализовать через класс IFormConverter
    def convert_data(self, game_mode, bo_type, seed, nickname) -> dict:
        '''Конвертирует полученные строчные данные в id'шники
        Принимает на вход строковые значения:
            * game_mode
            * bo_type
            * seed
        Возвращает словарь id:
            * game_mode_id
            * bo_type_id
            * seed
            NOTE seed указывает на team_id
        '''
        # game_mode = kwargs["game_mode"]
        # bo_type = kwargs["bo_type"]
        # seed = kwargs["seed"]
        # nickname = kwargs["nickname"]

        # TODO Разобраться как объединить все в один запрос.
        game_mode_id = Game_mode.query.filter_by(name=game_mode).first().id
        bo_type_id = Bo_type.query.filter_by(name=bo_type).first().id

        if seed == 'Opponent':
            seed = 2
        elif seed == 'You':
            seed = 1
        else:
            seed = random.choice([1,2])

        return  {
            'nickname': nickname,
            'game_mode_id': game_mode_id,
            'bo_type_id': bo_type_id,
            'seed': seed
        }
    
class JoinForm(FlaskForm):
    nickname = StringField(label=u"Nickname", validators=[DataRequired()])
    submit = SubmitField(label="Submit")

    # TODO Попробовать реализовать через класс IFormConverter
    # NOTE Если в форме заполняется только nickname то эта функция не нужна!!!
    def convert_data(self, room_uuid, nickname) -> dict:
        room_id = Room.query.filter_by(room_uuid=room_uuid).first().id
        return {"room_id": room_id, "nickname": nickname}

# TODO Убрать label, за ненадобностью?
class MapsForm(FlaskForm):
    map01 = BooleanField(label='awoken', default=False)
    map02 = BooleanField(label='corrupted', default=False)
    map03 = BooleanField(label='vale', default=False)
    map04 = BooleanField(label='molten', default=False)
    map05 = BooleanField(label='ruins', default=False)
    map06 = BooleanField(label='deep', default=False)
    map07 = BooleanField(label='exile', default=False)
    submit = SubmitField(label="Submit")


class ChampsForm(FlaskForm):
    # TODO Сделать по аналогии с MapsForm
    submit = SubmitField(label="Submit")