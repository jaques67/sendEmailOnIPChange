#!/usr/bin/python
import imaplib
import smtplib
import logging
from cryptography.fernet import Fernet
import ssl

from email.message import EmailMessage


class MailProcessing:
    logger = logging.getLogger(__name__)

    def __init__(self, config) -> None:
        """
        Initialisation of the MailProcessing class. The configuration file details
        are passed in as a dictionary, containing the login details and other required information
        to log into the email server - Only tested on Gmail
        :param config:
        :return: None
        """

        self.em = EmailMessage()

        login_details = dict(config['EMAIL_LOGIN'])
        encryption_details = dict(config['ENCRYPTION'])

        self.mail_username = login_details.get('username')
        self.mail_password = login_details.get('password')
        self.mail_port = login_details.get('port')
        self.mail_address = login_details.get('imap_address')

        self.sender = config['SEND_EMAIL']['from_address']
        self.receiver = config['SEND_EMAIL']['to_address']
        self.send_port = config['SEND_EMAIL']['port']
        self.send_server = config['SEND_EMAIL']['server_name']
        self.fern_key = encryption_details.get('key')

        self.selection = None
        self.mail = None
        self.data_type = None
        self.data = None
        MailProcessing.logger.info(f'MailProcessing has been initialised')

    def email_read_login(self):
        MailProcessing.logger.info(f'Logging into email')
        self.mail = imaplib.IMAP4_SSL(self.mail_address, self.mail_port)
        self.mail.login(self.mail_username, self.mail_password)
        MailProcessing.logger.info(f'Login successful')

    def find_unread_subject(self, subject: str) -> bool:
        """
        Connect to mail and search unread emails for a subject that
        corresponds to the value passed in for comparison.
        :param subject: string containing subject search criteria
        :return: bool
        """
        # subject="Resend IP Address"
        self.email_read_login()
        self.mail.select('Inbox')

        self.data_type, self.data = \
            self.mail.search(None, '(UNSEEN SUBJECT "%s")' % subject)

        # There is no new email requesting IP Address
        result = True
        if self.data_type == 'OK':
            if len(self.data[0]) == 0:
                result = False

        MailProcessing.logger.info(f'Unread mail with subject {subject} found: {result}')
        return result

    def mark_email_as_read(self):
        self.mail.store(self.data[0].decode('utf-8')
                        .replace(' ', ','), '+FLAGS', '\Seen')
        MailProcessing.logger.info(f'Updated mail to read')

    def encrypt_email_message(self, message):
        cipher_suite = Fernet(self.fern_key)  # f

        byte_string = bytes(message, 'utf-8')
        ciphered_text = cipher_suite.encrypt(byte_string)  # token

        MailProcessing.logger.info(f'Message has been encrypted')
        return ciphered_text

    def decrypt_email_message(self, message):
        cipher_suite = Fernet(self.fern_key)

        clear_message = cipher_suite.decrypt(message).decode()

        MailProcessing.logger.info(f'Message has been decrypted')
        return clear_message

    def send_email(self, subject, body):
        self.em['From'] = self.sender
        self.em['To'] = self.receiver
        self.em['Subject'] = subject
        self.em.set_content(body)
        context = ssl.create_default_context()

        with smtplib.SMTP_SSL(self.send_server, self.send_port, context=context) as smtp:
            smtp.login(self.mail_username, self.mail_password)
            smtp.sendmail(self.sender, self.receiver, self.em.as_string())
            MailProcessing.logger.info(f'Email has been sent from {self.sender} to {self.receiver}')
