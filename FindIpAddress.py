#!/usr/bin/python
# import socket
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import exists
# import urllib.request
import configparser
from cryptography.fernet import Fernet
import os
import time
import requests
import os
import configparser
from mailprocessing import MailProcessing



def get_old_ip_address(file_name):

    if not exists(file_name):
        print('ip config file does not exist')
        return "0.0.0.0"
    
    with open(file_name, "r") as file:
        old_ip_address = file.read()

    return old_ip_address


def get_current_ip_address(ip_check_service):

    # current_ip_address = urllib.request.urlopen(ip_check_service).read().decode('utf8')
    response = requests.get(ip_check_service)
    current_ip_address = response.text

    return current_ip_address


def write_current_ip_address(file_name):

    print('Writing ip config file')
    with open(file_name, "w") as f:
        f.write(ip_address)


def send_email(server_name, port_address, from_address, to_address, password, text):

    # Create a secure SSL context
    context = ssl.create_default_context()

    try:
        with smtplib.SMTP_SSL(server_name, port_address, context=context) as server:
            server.login(from_address, password)
            server.sendmail(from_address, to_address, text)
    except smtplib.SMTPAuthenticationError as e:
        print(f'Failed to send email. {e}')
        raise Exception("email authentication failed")
    except:
        print('some other error')


def create_email_message(new_ip_address, from_address, to_address):

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = "IP Address update"
     
    # body = encrypt_email_message(f"The new IP address is: {new_ip_address}")
    body = f"The new IP address is: {new_ip_address}"

    msg.attach(MIMEText(str(body)))
    text = msg.as_string()

    return text


def encrypt_email_message(body):

    fern_key = config['ENCRYPTION']['key']
    cipher_suite = Fernet(fern_key)  # f

    byte_string = bytes(body, 'utf-8')
    ciphered_text = cipher_suite.encrypt(byte_string)  # token

    return ciphered_text


def parse_config_file():

    # Read config
    config = configparser.ConfigParser()
    config.read('config.ini')
    print(f'config sections: {config.sections()}')
    return config


if __name__ == "__main__":
    
    # 
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    config = parse_config_file()

    time_out = int(config['GENERAL']['time_out'])
    username = config['READ_EMAIL']['username']
    imap_port = config['READ_EMAIL']['port']
    imap_address = config['READ_EMAIL']['imap_address']
    
    config_ip_address = dict(config['SEND_EMAIL'])
    file_name = config_ip_address.get('ip_config_file')

    ip_check_service = config['SEND_EMAIL']['ip_check_service']
    port_address = int(config['SEND_EMAIL']['port'])
    server_name = config['SEND_EMAIL']['server_name']

    from_address = config['EMAIL']['from_address']
    to_address = config['EMAIL']['to_address']
    password = config['EMAIL']['password']

    mail = MailProcessing(username, password, imap_port, imap_address)
    subject = 'Resend IP Address'

    while True:
        result = mail.resend_ip_address(subject)

        if result:
            print(f'Resending IP address.')
            # delete the file so that it can be resent
            if exists(file_name): 
                os.remove(file_name)
            mail.mark_email_as_read()

        # check ip info
        old_ip_address = get_old_ip_address(file_name)
        ip_address = get_current_ip_address(ip_check_service)

        if ip_address != old_ip_address:
            write_current_ip_address(file_name)
            text = create_email_message(ip_address, from_address, to_address)

            try:
                print('About to send email as ip addresses differed')
                send_email(server_name, port_address, from_address, to_address, password, text)
            except:
                break

        time.sleep(time_out)
