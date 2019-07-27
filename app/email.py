from flask_mail import Message
from app import mail, app
from flask import render_template


##
# @name: send_email
# @desc: takes in parameters and converts them into a Message and sends the message using flask_mail
##
def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    mail.send(msg)


##
# @name: send_password_reset_email
# @desc: generates a token and uses send_email() to send it to the user's email address
##
def send_password_reset_email(user):
    token = user.get_reset_password_token()
    send_email('[Microblog] Reset Your Password',
               sender=app.config['ADMINS'][0],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))
