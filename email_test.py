from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from credentials import email_login, linkedin_password, gmail_password
import imaplib
import email

import os
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials

# Scopes define the level of access you are requesting.
SCOPES = ['https://mail.google.com/']

def get_gmail_credentials():
    creds = None
    # The file token.json stores the user's access and refresh tokens.
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def scrape_linkedin_jobs(search_query):

    creds = get_gmail_credentials()
    # Use the access token as the password
    auth_string = 'user=%s\1auth=Bearer %s\1\1' % (email_login, creds.token)

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.authenticate('XOAUTH2', lambda x: auth_string)
    mail.select('inbox')

    # Search for emails
    result, data = mail.search(None, 'ALL')

    # Fetch Emails
    email_ids = data[0].split()
    email_ids.reverse()
    count = 0
    for e_id in email_ids:
        if count > 20:
            break
        result, email_data = mail.fetch(e_id, '(RFC822)')
        raw_email = email_data[0][1]
        # process the email
        # Example: Parsing the email content
        message = email.message_from_bytes(raw_email)
        if message["From"] == "LinkedIn <security-noreply@linkedin.com>" and "Here's your verification code" in message["Subject"]:
            verification_string = "Here's your verification code "
            print(message["Subject"][len(verification_string) :])
        print("__________________________________________________________________")
        count += 1



# Example usage
search_query = 'Software Engineer'
jobs = scrape_linkedin_jobs(search_query)
print(jobs)
