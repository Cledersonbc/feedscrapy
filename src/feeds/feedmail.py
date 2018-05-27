#!/usr/bin/env python3

"""
FeedScrapy is software that collect specifics news from a feed and
send it to an e-mail (or email list).
author: Clederson Cruz
Year: 2018
License: GNU GENERAL PUBLIC LICENSE (GPL)
"""

import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class Email:
    """
    Email receives info about subject, author,
    receiver and the message.
    """
    def __init__(self):
        self.msg = MIMEMultipart('alternative')

    def set_addr_to(self, addr_to):
        """
        Change the receiver's e-mail.
        :param addr_to: address to the receiver
        :return: None
        """
        del(self.msg['To']) # Delete old reference
        self.msg['To'] = addr_to

    def get_addr_to(self):
        """
        Get the receiver's address.
        :return: receiver's address
        """
        return self.msg['To']

    def set_addr_from(self, addr_from):
        """
        Set the author's address.
        :param addr_from: author's address
        :return: None
        """
        self.msg['From'] = addr_from

    def set_subject(self, subject):
        """
        Set the subject of the e-mail.
        :param subject: subject of the e-mail
        :return: None
        """
        self.msg['Subject'] = subject

    def attach_content(self, content):
        """
        Attach the e-mail's content (html content) in a MIMEText in the message.
        :param content: Content of this message
        :return: None
        """
        self.msg.attach(MIMEText(content, 'html'))

    def get_content(self):
        """
        Get the content of this message.
        :return: message's content
        """
        return self.msg


class SMTPServer:
    """
    SMTPServer creates a SMTP connection with
    provided server and authentication.
    """
    def __init__(self, server, port, user, password):
        self.server = server
        self.port = port
        self.user = user
        self.password = password

    def send(self, email):
        """
        Initalize the connection and try to send an Email.
        :param email: an Email to be sent
        :return: None
        """
        try:
            server = smtplib.SMTP(self.server, self.port)
            server.starttls()
            server.login(self.user, self.password)
            server.sendmail(self.user, email.get_addr_to(), email.get_content().as_string())
            server.quit()
        except:
            raise Exception('E-mail não enviado')