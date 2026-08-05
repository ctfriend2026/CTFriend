"""Email CTFriend login tokens to a list of users.

Reads an email list, provisions or looks up each token through the running
ctfriend container, and sends the token with SMTP settings from the environment.
"""

import sys
import time
import os
import smtplib, ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

# Load SMTP credentials and server settings from .env or the process environment.
load_dotenv()

if len(sys.argv) < 2:
    print("need email-list file")
    sys.exit(1)
    
def get_token_cmd(email):
    # Reuse the token manager inside the running app container.
    return f"docker exec ctfriend python3 app/token_manager.py whitelist {email} | awk -F': ' '/token is:/ {{print $2}}'"
    

email_file = sys.argv[1]
email_file = email_file.strip()

def create_token_email_message(sender_email, receiver_email, token):
    # Build a simple plaintext email with the user's login token.
    message = MIMEMultipart("alternative")
    message["Subject"] = "CTFriend Login Token"
    message["From"] = sender_email
    message["To"] = receiver_email
    
    text = f"""Hi {receiver_email},\nYour login token for CTFriend is {token}"""
    
    part = MIMEText(text, "plain")
    message.attach(part)
    
    return message.as_string()

def send_email(sender_email, receiver_email, message):
    # Send through SMTP with STARTTLS.
    port = 587

    username = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASS")
    smtp_server = os.getenv("SMTP_SERVER")

    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE

    try:
        server = smtplib.SMTP(smtp_server, port)
        server.ehlo() # Can be omitted
        server.starttls(context=context) # Secure the connection
        server.ehlo() # Can be omitted
        server.login(username, password)
        
        errs = server.sendmail(sender_email, receiver_email, message)
        print(f"Sending email to user: {receiver_email} - Errors: {errs}")
    except Exception as e:
        # Print any error messages to stdout
        print(e)
    finally:
        server.quit() 
##

sender_email = "ctfriend@ctf.internal"

with open(email_file, 'r') as file:
    for line in file:
        email = line.strip()
        
        if not email:
            continue
        
        token_cmd = get_token_cmd(email)
        # Run token generation one user at a time so each email gets its own token.
        token = os.popen(token_cmd).read()
        
        print(f"Got token: {token} for user {email}")
        
        email_message = create_token_email_message(sender_email, email, token)
        send_email(sender_email, email, email_message)
        
        time.sleep(5)
        
        
