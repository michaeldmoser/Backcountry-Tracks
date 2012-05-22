from wtforms import Form, validators, TextField, BooleanField

class LoginForm(Form):
    email = TextField(None, [validators.Required()])
    password = TextField(None, [validators.Required()])

class RegisterForm(Form):
    first_name = TextField(None, [validators.Required(message='Please provide a first name.')])
    last_name = TextField(None, [validators.Required(message='Please provide a last name.')])
    email = TextField(None, [
         validators.Required(message='Please provide an email address.'),
         validators.Email(message='Please provide a valid email address.')
         ])
    password = TextField(None, [validators.Required(message='Please provide a password')])
    password_again = TextField(None, [
        validators.Required(message='Please provide confirm password'),
        validators.EqualTo('password', message='Passwords do not match')
        ])
    birthdate = TextField(None, [validators.Regexp('^\d{4}-\d{1,2}-\d{1,2}', message='Birthdate is not complete.')])
    terms_agree = BooleanField(None, [validators.Required(message="You must agree to the Terms Of Use")])
