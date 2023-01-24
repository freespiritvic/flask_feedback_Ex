from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import InputRequired, Length, Email

class LoginForm(FlaskForm):
    """Login form."""
    username = StringField('Username',validators=[InputRequired(), Length(min=1, max=20)])
    password = PasswordField('Password',validators=[InputRequired(), Length(min=6, max=25)],)

class UserForm(FlaskForm):
    username = StringField("Username", validators=[InputRequired(), Length(min=1, max=20)])
    password = PasswordField("Password", validators=[InputRequired(), Length(min=6, max=25)])
    email = StringField("Email", validators=[InputRequired(), Email(), Length(max=60)])
    first_name = StringField("First Name", validators=[InputRequired(), Length(max=30)])
    last_name = StringField("Last Name", validators=[InputRequired(), Length(max=30)])

class FeedbackForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired(), Length(max=75)])
    content = StringField('Content', validators=[InputRequired(), Length(max=300)])

class DeleteForm(FlaskForm):
    """Delete form"""