#-*- coding:utf-8 -*-
from .user_db import Users

import click
from flask import current_app
from flask.cli import with_appcontext
from flask_mail import Message

@click.command('send-mail')
@click.option('--email-file')
@with_appcontext
def send_to_all_active(email_file):

    try:
        em = open(email_file).read().split("\n")
        subject = em[0]
        body = "\n".join(em[2:])

        if subject.strip() =="" or body.strip() == "":
            print("no subject '%s' \nor body \n%s" % (subject, body))
            return

        users = Users.get_active_users()
        print("noosletter \n----------")
        print("<subject>\n%s\n\n<body>\n%s\n----------" % (subject, body))
        print("send mail to %s  addresses \nContinue ?" % (len(users)))

        a = ""
        while a != "Y":
            a = input("Enter 'Y' to continue.  " )

        for i,user in enumerate(users):
            to = user[1]
            try:
                message = Message(sender=("noos-citoyen", "ne.pas.repondre@noos-citoyens.fr"))
                message.recipients = [to]
                message.body = body
                message.subject = subject
                print("sending message to %s   (%s/%s)" % (to, i, len(users)))
                current_app.mail.send(message)

            except Exception as err:
                print('ERR send mail %s %s \n %s' % (subject, to, err))

    except Exception as err:
        print (err)
