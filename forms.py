from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea

# Forms
class UserForm(FlaskForm):
    name = StringField("User Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(),
                                                     EqualTo("password_confirm", message="Passwords must match")])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired()])
    favorite_color = StringField("Favorite color")
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("User Name", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PasswordForm(FlaskForm):
    email = StringField("What is your email?", validators=[DataRequired()])
    password = PasswordField("What is your password?", validators=[DataRequired()])
    submit = SubmitField("Submit")

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    body = StringField("Body", validators=[DataRequired()], widget=TextArea())
    author = StringField("Author", validators=[DataRequired()])
    slug = StringField("Slug", validators=[DataRequired()])
    submit = SubmitField("Submit")