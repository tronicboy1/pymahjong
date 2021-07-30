from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,SelectField,RadioField,SelectMultipleField
from wtforms.validators import DataRequired,Regexp,Email,EqualTo,InputRequired


#Form for users to invite friends to game
class InviteFriend(FlaskForm):
    select_friend = SelectField("招待したい友達を選んでください")
    submit = SubmitField("招待する")

#form for users to send friend requests
class FriendRequest(FlaskForm):
    username = StringField('追加したいユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    submit = SubmitField('リクエストを送る')

#form to accept friend requests if user has new ones
class AcceptFriendRequest(FlaskForm):
    select_friend = SelectMultipleField("承諾したいリクエストを選んでください")
    submit = SubmitField("承諾する")

#form for users to join games invited
class JoinGame(FlaskForm):
    select_friend = SelectField("招待したい友達を選んでください")
    submit = SubmitField("招待する")
