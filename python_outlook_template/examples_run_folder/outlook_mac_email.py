# Created by: Michael Johnson - 11-21-2024
# # Initial Credit to
# https://stackoverflow[.]com/questions/61529817/automate-outlook-on-mac-with-python
# https://stackoverflow[.]com/users/6278428/jayme-gordon
# Seems to work with just appscript import (mactypes included in PiPI install of appscript) , but noted as unmaintained

from appscript import app, k
from mactypes import Alias
# from pathlib import Path

class Outlook(object):
    def __init__(self):
        self.client = app('Microsoft Outlook')


class Message(object):
    def __init__(self, parent=None, subject='', body='', to_recip=None, cc_recip=None, bcc_recip=None, show_=True):

        if parent is None:
            parent = Outlook()
        client = parent.client

        self.msg = client.make(
            new=k.outgoing_message,
            with_properties={k.subject: subject, k.content: body})

        if to_recip:
            self.add_recipients(emails=to_recip, type_='to')
        if cc_recip:
            self.add_recipients(emails=cc_recip, type_='cc')
        if bcc_recip:
            self.add_recipients(emails=bcc_recip, type_='bcc')

        if show_:
            self.show()

    def show(self):
        self.msg.open()
        self.msg.activate()

    def add_attachment(self, p):
        # p is a Path() obj, could also pass string

        p = Alias(str(p))  # convert string/path obj to POSIX/mactypes path

        self.msg.make(new=k.attachment, with_properties={k.file: p})

    def add_recipients(self, emails, type_='to'):
        if not isinstance(emails, list):
            emails = [emails]
        for email in emails:
            self.add_recipient(email=email, type_=type_)

    def add_recipient(self, email, type_='to'):
        msg = self.msg
        recipient = None

        if type_ == 'to':
            recipient = k.to_recipient
        elif type_ == 'cc':
            recipient = k.cc_recipient
        elif type_ == 'bcc':
            recipient = k.bcc_recipient

        msg.make(new=recipient, with_properties={k.email_address: {k.address: email}})

# Sample section to attach file - Would need to be integrated into script

# def create_message_with_attachment():
#     subject = 'This is an important email!'
#     body = 'Just kidding its not.'
#     to_recip = ['user@example.com', 'user2@example.com']
#
#     msg = Message(subject=subject, body=body, to_recip=to_recip)
#
#     # attach file
#     # p = Path('path/to/myfile.pdf')
#     # msg.add_attachment(p)
#
#     msg.show()
