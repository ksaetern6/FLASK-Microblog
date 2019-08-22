from flask import render_template, current_app
from flask_babel import _
from app.email import send_email


##
# @name: send_password_reset_email
# @desc: generates a token and uses send_email() to send it to the user's email address
##
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email(_('[Microblog] Reset Your Password'),
               sender=current_app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

