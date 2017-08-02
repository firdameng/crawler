
# -*- coding: utf-8 -*-
import smtplib
import email.utils
from email.mime.text import MIMEText

# Prompt the user for connection info
servername = 'smtp.163.com'
username = 'caiwencheng95@163.com'
password = 'cai4739027'   # login at the other client

# Create the message
msg = MIMEText('Test message from cwc')
msg['Subject'] = 'Test from cwc'
recipients = ['1546233608@qq.com','15623780837@163.com']

msg['To'] = ", ".join(recipients)
msg['From'] = email.utils.formataddr(('Auther', username))


server = smtplib.SMTP(servername)

try:
    server.set_debuglevel(True)

    # identify ourselves, prompting server for supported features
    server.ehlo()

    # If we can encrypt this session, do it
    if server.has_extn('STARTTLS'):
        server.starttls()
        server.ehlo() # re-identify ourselves over TLS connection

    server.login(username, password)
    server.sendmail(username, recipients, msg.as_string())
finally:
    server.quit()    