from flask_wtf import FlaskForm
from wtforms import StringField,SubmitField,PasswordField,SelectField,RadioField,SelectMultipleField
from wtforms.validators import Regexp,Email,EqualTo,InputRequired
from wtforms import ValidationError


class Login(FlaskForm):
    #Username and paassword will be checked to have value
    username = StringField('ユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$',message='英数字のみ入力可能')])
    password = PasswordField('パスワード：',validators=[InputRequired()])
    submit = SubmitField('ログイン')

#form for user sign up with checks on input
class SignUp(FlaskForm):
    #email validator to check email is correct format
    email_address = StringField('メールアドレス：',validators=[InputRequired(),Email()])
    password = PasswordField('パスワード：',validators=[InputRequired(),EqualTo('password_confirm',message='パスワードは一致していません')])
    password_confirm = PasswordField('パスワード再入力：',validators=[InputRequired()])
    #confirms username has correct characters
    username = StringField('ユーザーネーム：',validators=[InputRequired(),Regexp('^\w+$')])
    submit = SubmitField('登録')

    def check_email(self,field):
        if UserData.query.filter_by(email_address=field.data).first():
            raise ValidationError('入力したメールアドレスは既に登録されているようです')

    def check_username(self,field):
        if UserData.query.filter_by(username=field.data).first():
            raise ValidationError('入力したユーザーネームは既に登録されているようです')
