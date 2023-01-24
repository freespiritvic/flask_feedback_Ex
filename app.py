from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import db, connect_db, User, Feedback
from forms import LoginForm, UserForm, FeedbackForm, DeleteForm
from sqlalchemy.exc import IntegrityError
from werkzeug.exceptions import Unauthorized

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///flask_feedback_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "flask_F33db@cK"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

connect_db(app)
app.app_context().push()

# db.drop_all()
db.create_all()

toolbar = DebugToolbarExtension(app)

@app.route('/')
def home_page():
    """Redirect user to register"""
    return redirect('/login')

@app.route('/register', methods=['GET', 'POST'])
def register(): 
    """Render register page for user"""
    if 'username' in session:   
        return redirect(f"/users/{session['username']}")

    form = UserForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        email = form.email.data
        first_name = form.first_name.data
        last_name = form.last_name.data
        new_user = User.register(username, password, email, first_name, last_name)

        db.session.add(new_user)
        try:
            db.session.commit()
        except IntegrityError:
            form.username.errors.append('Username taken. Please pick another')
            return render_template('register.html', form=form)

        session['username'] = new_user.username
        flash('Welcome! Successfully Created Your Account!', 'success')
        return redirect(f'/users/{session["username"]}')

    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Login returning user"""
    if 'username' in session:   
        return redirect(f"/users/{session['username']}")

    form = LoginForm()

    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user = User.authenticate(username, password)

        if user:
            flash(f'Welcome Back, {user.username}!', 'primary')
            session['username'] = user.username
            return redirect(f'/users/{user.username}')
        else:
            form.username.errors = ['Invalid username/password']
            return render_template('login.html', form=form)

    return render_template('login.html', form=form)

@app.route('/logout')
def logout():
    """Logs user out and redirects to homepage."""
    session.pop('username', None)
    return redirect('/login')

# @app.route('/secret')
# def secret():
#     """Example hidden page for logged-in users only."""

#     if 'user_username' not in session:
#         flash('You must be logged in to view!', 'error')
#         return redirect('/')
#     else:
#         return render_template('secret.html')

@app.route('/users/<username>')
def show_user(username):
    """User detail page"""
    if 'username' in session:
        if username != session['username']:
            raise Unauthorized()

        form = DeleteForm()
        user = User.query.get(session['username'])
        return render_template('show.html', form=form, user=user)
    else:
        flash('Must be logged in', 'label alert')
        return redirect('/login')

@app.route('/users/<username>/delete', methods=['POST'])
def delete_user(username):
    """Delete User"""

    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    user = User.query.get_or_404(username)
    db.session.delete(user)
    db.session.commit()
    session.pop('username', None)

    return redirect('/login')

@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def add_feedback(username):
    """Add a new piece of feedback"""
    if 'username' not in session or username != session['username']:
        raise Unauthorized()

    form = FeedbackForm()

    if form.validate_on_submit():
        title = form.title.data
        content = form.content.data
        feedback = Feedback(title=title, content=content, username=username)

        db.session.add(feedback)
        db.session.commit()
        return redirect(f'/users/{feedback.username}')
    
    return render_template('feedback.html', form=form)

@app.route('/feedback/<feedback_id>/update', methods=['GET', 'POST'])
def update_user(feedback_id):
    """Update User"""
    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()
    
    form = FeedbackForm(obj=feedback)

    if form.validate_on_submit():
        feedback.title = form.title.data
        feedback.content = form.content.data

        db.session.commit()

        return redirect(f"/users/{feedback.username}")

    return render_template('/edit.html', form=form, feedback=feedback)

@app.route('/feedback/<feedback_id>/delete', methods=['POST'])
def delete_feedback(feedback_id):
    """Delete Feedback"""
    feedback = Feedback.query.get_or_404(feedback_id)

    if 'username' not in session or feedback.username != session['username']:
        raise Unauthorized()
  
    form = DeleteForm()

    if form.validate_on_submit():
        db.session.delete(feedback)
        db.session.commit()
        
    return redirect(f'/users/{feedback.username}')
