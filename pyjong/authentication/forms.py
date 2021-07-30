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
