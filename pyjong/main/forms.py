from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,SelectField,RadioField,SelectMultipleField,TextField
from wtforms.validators import DataRequired,Regexp,Email,EqualTo,InputRequired

class InviteFriend(FlaskForm):
    select_friend = SelectField("招待する友達",validators=[InputRequired()])
    room_name = TextField("パーティー名：",validators=[InputRequired(),Regexp('^\w+$',message="英数字のみ入力可能")])
    submit = SubmitField("パーティーへ招待する")

#form to start solo played
class PlaySolo(FlaskForm):
    solo_submit = SubmitField("一人で麻雀を始める")

class LeaveRoom(FlaskForm):
    leave_submit = SubmitField("雀荘を退室")

#form for users to send friend requests
class FriendRequest(FlaskForm):
    username = StringField('追加したいユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    submit = SubmitField('リクエストを送る')

#form to accept friend requests if user has new ones
class AcceptFriendRequest(FlaskForm):
    select_friend = SelectMultipleField("承諾したいリクエストを選んでください")
    submit = SubmitField("承諾する")

#deletes user selected
class DeleteFriend(FlaskForm):
    select_friend = SelectField("承諾したいリクエストを選んでください")
    submit = SubmitField("削除")

class AcceptInvite(FlaskForm):
    select_friend = SelectField("承諾したい招待を選んでください")
    submit = SubmitField("パーティーに入る")
