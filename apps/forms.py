from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,SelectField,RadioField,SelectMultipleField
from wtforms.validators import DataRequired,Regexp,Email,EqualTo,InputRequired


class Login(FlaskForm):
    #Username and paassword will be checked to have value
    username = StringField('ユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    password = PasswordField('パスワード：',validators=[InputRequired()])
    submit = SubmitField('ログイン')

#form for user sign up with checks on input
class SignUp(FlaskForm):
    #email validator to check email is correct format
    email_address = StringField('メールアドレス：',validators=[InputRequired(),Email("正しいメールアドレスを入力してください")])
    password = PasswordField('パスワード：',validators=[InputRequired()])
    #confirms username has correct characters
    username = StringField('ユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    submit = SubmitField('登録')

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
