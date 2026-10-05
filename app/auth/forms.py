from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length, Regexp


class LoginForm(FlaskForm):
    identity = StringField(
        "Email or username", validators=[DataRequired(), Length(max=254)]
    )
    password = PasswordField("Password", validators=[DataRequired(), Length(max=128)])
    remember = BooleanField("Remember me")
    submit = SubmitField("Sign in")


class RegisterForm(FlaskForm):
    username = StringField(
        "Username",
        validators=[
            DataRequired(),
            Length(min=3, max=40),
            Regexp(
                r"^[a-zA-Z0-9_]+$", message="Use letters, numbers and underscores only."
            ),
        ],
    )
    email = StringField(
        "Email address", validators=[DataRequired(), Email(), Length(max=254)]
    )
    password = PasswordField(
        "Password", validators=[DataRequired(), Length(min=8, max=128)]
    )
    confirm_password = PasswordField(
        "Confirm password",
        validators=[
            DataRequired(),
            EqualTo("password", message="Passwords must match."),
        ],
    )
    submit = SubmitField("Create account")


class ProfileForm(FlaskForm):
    email = StringField(
        "Email address", validators=[DataRequired(), Email(), Length(max=254)]
    )
    submit = SubmitField("Save changes")


class PasswordForm(FlaskForm):
    current_password = PasswordField(
        "Current password", validators=[DataRequired(), Length(max=128)]
    )
    new_password = PasswordField(
        "New password", validators=[DataRequired(), Length(min=8, max=128)]
    )
    confirm_password = PasswordField(
        "Confirm new password", validators=[DataRequired(), EqualTo("new_password")]
    )
    submit = SubmitField("Update password")
