from main import db
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin


# Models
class users_data(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(16), nullable=False, unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    email = db.Column(db.String(255), nullable=False, unique=True)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    favorite_color = db.Column(db.String(32))
    posts = db.relationship("Post", backref="user", cascade="all, delete-orphan")

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
    author = db.Column(db.Integer, db.ForeignKey('users_data.id'))
    create_time = db.Column(db.DateTime, default=datetime.utcnow)
    slug = db.Column(db.String(50))
    pictures = db.relationship("Picture", backref="my_post", cascade="all, delete-orphan")


class Picture(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    post = db.Column(db.Integer, db.ForeignKey('post.id'))
    url = db.Column(db.String(20), nullable=False)
    create_time = db.Column(db.DateTime, default=datetime.utcnow)