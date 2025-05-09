from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, SelectField, FloatField
from wtforms.validators import DataRequired, Email, EqualTo, Length, ValidationError, NumberRange
from email_validator import validate_email, EmailNotValidError
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Sign In')

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=4, max=64)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=8)])
    password2 = PasswordField('Repeat Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Register')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('Please use a different username.')
            
    def validate_email(self, email):
        try:
            # Validate the email format
            validate_email(email.data)
            # Check if email is already registered
            user = User.query.filter_by(email=email.data).first()
            if user is not None:
                raise ValidationError('Please use a different email address.')
        except EmailNotValidError as e:
            raise ValidationError('Please enter a valid email address.')

class CreateWalletForm(FlaskForm):
    name = StringField('Wallet Name', validators=[DataRequired()])
    blockchain = SelectField('Blockchain', choices=[
        ('ethereum', 'Ethereum'),
        ('bitcoin', 'Bitcoin'),
        ('binance', 'Binance Smart Chain'),
        ('hamster-eth', 'Hamster (Ethereum)'),
        ('hamster-bsc', 'Hamster (BSC)'),
        ('usdt-eth', 'Tether USDT (Ethereum)'),
        ('usdt-bsc', 'Tether USDT (BSC)')
    ], validators=[DataRequired()])
    submit = SubmitField('Create Wallet')

class SendTransactionForm(FlaskForm):
    recipient_address = StringField('Recipient Address', validators=[
        DataRequired(),
        Length(min=26, max=42, message='Address must be between 26 and 42 characters')
    ])
    amount = FloatField('Amount', validators=[
        DataRequired(),
        NumberRange(min=0.0001, message='Amount must be greater than 0.0001')
    ])
    fee = FloatField('Transaction Fee', validators=[
        DataRequired(),
        NumberRange(min=0.0001, message='Fee must be greater than 0.0001')
    ])
    submit = SubmitField('Send')
