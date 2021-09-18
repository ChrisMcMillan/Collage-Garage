from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, FileField, BooleanField
from wtforms.validators import DataRequired, EqualTo, Length
from wtforms.widgets import TextArea
from flask_wtf.file import FileField, FileAllowed

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

class PostForm(FlaskForm):
    title = StringField("Title", validators=[DataRequired()])
    body = StringField("Body", validators=[DataRequired()], widget=TextArea())
    # picture = FileField("Picture", validators=[FileAllowed(['png', 'jpg'])])
    published = BooleanField("Published")
    submit = SubmitField("Submit")

class PictureForm(FlaskForm):
    picture = FileField("Picture", validators=[DataRequired(), FileAllowed(['png', 'jpg'])])
    upload = SubmitField("Upload")