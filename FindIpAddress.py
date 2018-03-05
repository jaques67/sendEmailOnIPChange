import socket
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def get_old_ip_address():
    with open("ip_address.ini", "r") as file:
        old_ip_address = file.read()

    return old_ip_address


def get_current_ip_address():
    # https://www.w3resource.com/python-exercises/python-basic-exercise-55.php
    current_ip_address = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2]
    if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)),
    s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET,
    socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

    return current_ip_address


def send_email(new_ip_address):
    from_address = "gmail email address"
    to_address = "recipient email address"
    msg = MIMEMultipart()
    msg['From'] = from_address
    msg['To'] = to_address
    msg['Subject'] = "IP Address update"
     
    body = "The new IP address is: " + new_ip_address
    msg.attach(MIMEText(body, 'plain'))
     
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    server.login(from_address, "place gmail password here")
    text = msg.as_string()
    server.sendmail(from_address, to_address, text)
    server.quit()
    
    
if __name__ == "__main__":
    old_ip_address = get_old_ip_address()
    ip_address = get_current_ip_address()

    if ip_address != old_ip_address:
        with open("ip_address.ini", "w") as f:
            f.write(ip_address)
    
        send_email(ip_address)
