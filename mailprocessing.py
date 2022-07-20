
import imaplib  


class MailProcessing:
    
    def __init__(self, username, password, port, address) -> None:
        self.gmail_username = username
        self.gmail_password = password
        self.gmail_port = port
        self.gmail_address = address
        self.selection = None
        self.gmail = None
        self.data_type = None
        self.data = None

    def resend_ip_address(self, subject):
        # subject="Resend IP Address"
        self.gmail = imaplib.IMAP4_SSL(self.gmail_address, self.gmail_port)
        self.gmail.login(self.gmail_username, self.gmail_password)
        self.gmail.select('Inbox')
        self.data_type, self.data = self.gmail.search(None, '(UNSEEN SUBJECT "%s")' % subject)
        
        # There is no new email requesting IP Address
        result = True
        if self.data_type == 'OK':
            if len(self.data[0]) == 0:
                result = False

        return result

    def mark_email_as_read(self):
        self.gmail.store(self.data[0].decode('utf-8').replace(' ',','),'+FLAGS','\Seen')
