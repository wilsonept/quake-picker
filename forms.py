from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired, AnyOf




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

    
class JoinForm(FlaskForm):
    nickname = StringField(label=u"Nickname", validators=[DataRequired()])
    submit = SubmitField(label="Submit")


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