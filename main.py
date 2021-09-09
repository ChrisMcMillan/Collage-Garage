from flask import Flask, render_template, flash, request
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_migrate import Migrate

app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:BFKJYddpxVT23Zy@localhost:3306/users'
app.config['SECRET_KEY'] = "the secret key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class users_data(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False)
    password = db.Column(db.String(32), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    favorite_color = db.Column(db.String(32))

    def __repr__(self):
        return '<Name %r>' % self.username

# Form Class
class UserForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired()])
    email = StringField("Email", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    favorite_color = StringField("Favorite color", validators=[DataRequired()])
    submit = SubmitField("Submit")

class NameInputForm(FlaskForm):
    name = StringField("What is your name?", validators=[DataRequired()])
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


@app.route('/name', methods=['GET', 'POST'])
def name():
    name = None
    form = NameInputForm()

    if form.validate_on_submit():
        name = form.name.data
        form.name.data = ''
        flash("Form submitted successfully!")

    return render_template("name.html", name=name, form=form)

@app.route('/user/add', methods=['GET', 'POST'])
def add_user():
    form = UserForm()
    name = None

    if form.validate_on_submit():
        user = users_data.query.filter_by(email=form.email.data).first()

        if user == None:
            user = users_data(username=form.name.data, email=form.email.data,
                              password=form.password.data, favorite_color=form.favorite_color.data)
            db.session.add(user)
            db.session.commit()

        name = form.name.data
        form.name.data = ''
        form.email.data = ''
        form.password.data = ''
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
