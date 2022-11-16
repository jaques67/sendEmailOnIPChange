#!/usr/bin/python
import configparser
import os
import shutil
import time
import logging
from datetime import datetime
from dotenv import load_dotenv
import dotenv

from cryptography.fernet import Fernet

from ipInfo import IpInfo
from mailprocessing import MailProcessing

debug = False


def parse_config_file(file_name) -> configparser:
    # Read config
    config_file = configparser.ConfigParser()
    config_file.read(file_name)

    if debug:
        print(f'config sections: {config_file.sections()}')

    return config_file


def update_config_file(filename) -> None:
    # Write the new structure to the new file
    modifiedTime = os.path.getmtime(filename)
    timestamp = datetime.fromtimestamp(modifiedTime).strftime("%b-%d-%Y_%H.%M.%S")

    if os.path.exists(filename):
        shutil.copy(filename, f'{filename}.{timestamp}')
    with open(filename, 'w') as configfile:
        config.write(configfile)


def generate_fernet_key() -> bytes:
    key = Fernet.generate_key()

    return key


def create_fernet_environment_variable(dotenv_file):
    new_key = generate_fernet_key()

    os.environ['FERNET_KEY'] = new_key.decode('UTF-8')
    if len(dotenv_file) > 0:
        # Don't write to .env file as it does not exist
        dotenv.set_key(dotenv_file, "FERNET_KEY", os.environ["FERNET_KEY"])

    return os.environ.get('FERNET_KEY')


def get_fernet_environment_variable():
    key_gen = False
    file_exist = True
    dotenv_file = dotenv.find_dotenv()

    if len(dotenv_file) == 0:
        file_exist = False
    load_dotenv(dotenv_file)

    old_key = os.environ.get('FERNET_KEY')
    if old_key is None or old_key == 'None':
        old_key = create_fernet_environment_variable(dotenv_file)
        key_gen = True

    return old_key, key_gen, file_exist


def encrypt_string(data, key):
    cipher_suite = Fernet(key.encode('utf-8'))
    ciphered_text = cipher_suite.encrypt(data.encode('utf-8'))

    return ciphered_text


def decrypt_string(data, key):
    cipher_suite = Fernet(key.encode('utf-8'))
    clear_message = cipher_suite.decrypt(data).decode()

    return clear_message


def main() -> None:
    time_out = int(config['GENERAL']['time_out'])

    ip_info = IpInfo(config)
    mail = MailProcessing(config)
    subject = 'Resend IP Address'

    # Infinite loop to check the IP address as specified in the time_out variable as found in the config file.
    while True:
        # Is there an email request asking for the IP address to be sent?
        result = mail.find_unread_subject(subject)

        if result:
            logger.info("Resending IP address.")
            if debug:
                print(f'Resending IP address.')

            # delete the file so that it can be resent
            ip_info.delete_ip_file()
            mail.mark_email_as_read()

        if ip_info.different_ip_address():

            try:
                logger.info("About to send email as ip addresses differed.")
                if debug:
                    print('About to send email as ip addresses differed')

                send_mail = MailProcessing(config)

                subject = "IP Address update"
                body = f"The new IP address is: {ip_info.get_current_ip_address()}"
                logger.debug(body)

                send_mail.send_email(subject, body)
                del send_mail
            except KeyboardInterrupt:
                break
            except Exception as e:
                print(f'Exception occurred: {e}')
                raise

        time.sleep(time_out)


if __name__ == "__main__":
    # change the program path to the real path processing from.
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    file_name = 'config.ini'
    config = parse_config_file(file_name)

    fernet_key = config['ENCRYPTION']['key']

    logging.basicConfig(filename="log.txt", level=logging.DEBUG, format="%(asctime)s %(message)s")  # , filemode="w")
    logger = logging.getLogger('ip_logs')

    # Preference is given to reading from the config file. If it does not exist on the config file it will try and
    # read the value from the .env file.
    # Enable write_key if you want to write the fernet key to your config.ini file
    write_key = config['ENCRYPTION']['False']
    if write_key == 'False':
        write_key = False
    else:
        write_key = True

    if fernet_key is None or fernet_key == 'None':
        # Try reading from environment file
        fernet_key, key_generated, file_exists = get_fernet_environment_variable()
        print(f'fernet key: {fernet_key}')

        # A new key was generated. Assume that the password on the file is open, so encrypt and save it to the
        # config.ini file
        password = config['EMAIL_LOGIN']['password']
        if key_generated:
            encrypted_password = encrypt_string(password, fernet_key)
            config.set('EMAIL_LOGIN', 'password', encrypted_password.decode('utf-8'))
            update_config_file(file_name)
            print(config['EMAIL_LOGIN']['password'])

        # password was encrypted so decrypt it
        print(f'fernet key 2: {fernet_key}')
        decrypted_password = decrypt_string(config['EMAIL_LOGIN']['password'], fernet_key)
        print(f'decrypted password: {decrypted_password}')
        config['EMAIL_LOGIN']['password'] = decrypted_password
        print(config['EMAIL_LOGIN']['password'])

        # if a key was generated and the .env file does not exist, force a write to the config file.
        if (key_generated and not file_exists) or (key_generated and write_key):
            config.set('ENCRYPTION', 'key', fernet_key)
            update_config_file(file_name)
    main()
