import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

# Populate details of the Sender and Receiver of the emails
address_of_sender = 'ispyteam12345@gmail.com'
address_of_receiver = 'stars.keeper@yahoo.com'
password_of_sender = 'ispyteam012.'

# Populate the email fields
email = MIMEMultipart()
email['From'] = address_of_sender
email['To'] = address_of_receiver
email['Subject'] = 'A test mail sent by iSpy Team Project'
mail_content = '''Test Email
This is a test email triggered by the detection of motion from the raspberry pi camera.
'''
email.attach(MIMEText(mail_content, 'plain'))

# Create and use smtp Session to send the email
current_session = smtplib.SMTP('smtp.gmail.com', 587)
current_session.starttls()
current_session.login(address_of_sender, password_of_sender)
email_content = email.as_string()
current_session.sendmail(address_of_sender, address_of_receiver, email_content)

# Destroy session
current_session.quit()
