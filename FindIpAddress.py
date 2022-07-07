#!/usr/bin python
import socket
import smtplib
import ssl
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import exists
import urllib.request
import configparser
from cryptography.fernet import Fernet


def get_old_ip_address(file_name):

    if not exists(file_name):
        return "0.0.0.0"
    
    with open(file_name, "r") as file:
        old_ip_address = file.read()

    return old_ip_address


def get_current_ip_address(ip_check_service):

    current_ip_address = urllib.request.urlopen(ip_check_service).read().decode('utf8')

    return current_ip_address


def send_email(server_name, port_address, from_address, to_address, password, text):

    # Create a secure SSL context
    context = ssl.create_default_context()

    with smtplib.SMTP_SSL(server_name, port_address, context=context) as server:
        server.login(from_address, password)
        server.sendmail(from_address, to_address, text)
    

def create_email_message(new_ip_address, from_address, to_address):

    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = "IP Address update"
     
    body = encrypt_email_message(f"The new IP address is: {new_ip_address}")

    msg.attach(MIMEText(str(body)))
    text = msg.as_string()

    return text


def encrypt_email_message(body):

    fern_key = config['ENCRYPTION']['key']
    cipher_suite = Fernet(fern_key)  # f

    byte_string = bytes(body, 'utf-8')
    ciphered_text = cipher_suite.encrypt(byte_string)  # token

    return ciphered_text


def write_current_ip_address(file_name):

    with open(file_name, "w") as f:
        f.write(ip_address)


def parse_config_file():

    # Read config
    config = configparser.ConfigParser()
    config.read('config.ini')

    return config


if __name__ == "__main__":
    
    config = parse_config_file()

    file_name = config['IP_ADDRESS']['ip_config_file']

    ip_check_service = config['IP_ADDRESS']['ip_check_service']
    port_address = int(config['IP_ADDRESS']['port'])
    server_name = config['IP_ADDRESS']['server_name']

    from_address = config['EMAIL']['from_address']
    to_address = config['EMAIL']['to_address']
    password = config['EMAIL']['password']

    old_ip_address = get_old_ip_address(file_name)
    ip_address = get_current_ip_address(ip_check_service)

    if ip_address != old_ip_address:
        write_current_ip_address(file_name)
        text = create_email_message(ip_address, from_address, to_address)
        print('about to send email')
        send_email(server_name, port_address, from_address, to_address, password, text)
