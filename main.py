from flask import Flask, render_template, flash, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from werkzeug.security import generate_password_hash
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from forms import UserForm, LoginForm, PostForm


app = Flask(__name__)

# app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:BFKJYddpxVT23Zy@localhost:3306/users'
app.config['SECRET_KEY'] = "the secret key"

db = SQLAlchemy(app)
migrate = Migrate(app, db)
from models import users_data, Post

# Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return users_data.query.get(int(user_id))

@app.route('/')
def index():
    return render_template("index.html")

@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.errorhandler(500)
def page_not_found(e):
    return render_template("500.html"), 500

@app.route('/add_post', methods=['GET', 'POST'])
@login_required
def add_post():

    form = PostForm()

    if form.validate_on_submit():

        new_post = Post(title=form.title.data, author=current_user.id, body=form.body.data, slug=form.slug.data)

        db.session.add(new_post)
        db.session.commit()

        form.title.data = ''
        form.body.data = ''
        form.slug.data = ''

        flash("Form submitted successfully!")

    return render_template("add_post.html", form=form)


@app.route('/all_posts', methods=['GET'])
def all_posts():

    results = db.session.query(Post, users_data).\
        join(users_data).filter(Post.author == users_data.id)\
        .with_entities(Post.id.label('post_id'), Post.title, Post.body, Post.create_time, users_data.username)

    # for post in results:
     #   print(post.post_id, post.title, post.body, post.create_time, post.username)

    return render_template("show_posts.html", all_posts=results)


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


@app.route('/post_page/<int:id>', methods=['GET'])
def post_page(id):

    post = Post.query.get_or_404(id)

    author = users_data.query.get_or_404(post.author)

    return render_template("post_page.html",  post=post, author=author)

@app.route('/update_post/<int:id>', methods=['GET', 'POST'])
@login_required
def update_post(id):
    form = PostForm()
    post_to_update = Post.query.get_or_404(id)
    author = users_data.query.get_or_404(post_to_update.author)

    if form.validate_on_submit():

        post_to_update.title = form.title.data
        post_to_update.body = form.body.data
        post_to_update.slug = form.slug.data

        db.session.add(post_to_update)
        db.session.commit()

        flash("Post Updated Successfully!")

        return redirect(url_for('post_page', id=post_to_update.id))

    form.title.data = post_to_update.title
    form.body.data = post_to_update.body
    form.slug.data = post_to_update.slug

    return render_template("update_post.html", form=form, post_to_update=post_to_update, author=author)



@app.route('/user/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update_user(id):
    form = UserForm()
    user_to_update = users_data.query.get_or_404(id)

    if request.method == "POST":
        user_to_update.username = request.form['name']
        user_to_update.email = request.form['email']
        user_to_update.favorite_color = request.form['favorite_color']

        try:
            db.session.commit()
            flash("User Updated Successfully!")
            return render_template("update_user.html", form=form, user_to_update=user_to_update)

        except:
            flash("Failed to update user")
            return render_template("update_user.html", form=form, user_to_update=user_to_update)

    else:
        return render_template("update_user.html", form=form, user_to_update=user_to_update)


@app.route('/user/delete/<int:id>')
@login_required
def delete_user(id):
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


@app.route('/posts/delete/<int:id>')
@login_required
def delete_post(id):

    post_to_delete = Post.query.get_or_404(id)

    try:
        db.session.delete(post_to_delete)
        db.session.commit()
        flash("Post Deleted Successfully!")

        return redirect(url_for('all_posts'))

    except:

        flash("Error: Could not delete post.")
        return redirect(url_for('all_posts'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = users_data.query.filter_by(username=form.username.data).first()

        if user:
            if user.verify_password(form.password.data):
                login_user(user)
                flash("Login Successful")
                return redirect(url_for('dashboard'))
            else:
                flash("Wrong Password")

        else:
            flash("User not found")

    return render_template('login.html', form=form)

@app.route('/logout', methods=['GET', 'POST'])
@login_required
def logout():
    logout_user()
    flash("You have been logged out")
    return redirect(url_for('login'))

@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():

    return render_template('user_dashboard.html')