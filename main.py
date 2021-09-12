from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, PasswordField, BooleanField, ValidationError
from wtforms.validators import DataRequired, EqualTo, Length
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash, check_password_hash
from wtforms.widgets import TextArea

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:BFKJYddpxVT23Zy@localhost:3306/users'
app.config['SECRET_KEY'] = "the secret key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Models

class users_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    favorite_color = db.Column(db.String(32))

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return '<Name %r>' % self.username

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(50), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(50), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(50))

# Forms
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired(),
                                                     EqualTo("password_confirm", message="Passwords must match")])
    password_confirm = PasswordField("Confirm Password", validators=[DataRequired()])
    favorite_color = StringField("Favorite color")
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

@app.route('/')
def index():
    return render_template("index.html")

@app.route('/user/<name>')
def user(name):
    return render_template("user.html", user_name=name)

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/add_post', methods=['GET', 'POST'])
def add_post():

    form = PostForm()

    if form.validate_on_submit():

        new_post = Post(title=form.title.data, body=form.body.data, author=form.author.data, slug=form.slug.data)

        db.session.add(new_post)
        db.session.commit()

        form.title.data = ''
        form.body.data = ''
        form.author.data = ''
        form.slug.data = ''

        flash("Form submitted successfully!")

    return render_template("add_post.html", form=form)

@app.route('/test_pw', methods=['GET', 'POST'])
def test_pw():
    email = None
    password = None
    pw_to_check = None
    passed = None
    form = PasswordForm()

    if form.validate_on_submit():
        email = form.email.data
        password = form.password.data

        form.email.data = ''
        form.password.data = ''

        pw_to_check = users_data.query.filter_by(email=email).first()

        if pw_to_check:
            passed = pw_to_check.verify_password(password)

        flash("Form submitted successfully!")

    return render_template("test_pw.html", email=email, password=password, passed=passed,
                           pw_to_check=pw_to_check, form=form)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    name = None

    if form.validate_on_submit():
        user = users_data.query.filter_by(email=form.email.data).first()

        # If a user with the email does not already exist
        if user == None:
            hashed_pw = generate_password_hash(form.password.data, "sha256")
            user = users_data(username=form.name.data, email=form.email.data,
                              password_hash=hashed_pw, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()

        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password.data = ''
        form.password_confirm.data = ''
        form.favorite_color.data = ''
        flash("Form submitted successfully!")

    our_users = users_data.query.order_by(users_data.create_time)
    return render_template("add_user.html", form=form, name=name, our_users=our_users)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    form = UserForm()
    name_to_update = users_data.query.get_or_404(id)

    if request.method == "POST":
        name_to_update.username = request.form['name']
        name_to_update.email = request.form['email']
        name_to_update.favorite_color = request.form['favorite_color']

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update.html", form=form, name_to_update=name_to_update)

        except:
            flash("Failed to update user")
            return render_template("update.html", form=form, name_to_update=name_to_update)

    else:
        return render_template("update.html", form=form, name_to_update=name_to_update)


@app.route('/delete/<int:id>')
def delete(id):
    user_to_delete = users_data.query.get_or_404(id)
    form = UserForm()
    name = None

    try:
        db.session.delete(user_to_delete)
        db.session.commit()
        flash("User Deleted Successfully!")

        our_users = users_data.query.order_by(users_data.create_time)
        return render_template("add_user.html", form=form, name=name, our_users=our_users)

    except:

        flash("Error: Could not delete user.")
        return render_template("add_user.html", form=form, name=name, our_users=our_users)

