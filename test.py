# modules
import imaplib
import email
import re

import html_text
import pyttsx3
from email.header import decode_header

username = "vasantharaja200295@gmail.com"

# generated app password
app_password = "tyirdyxbiunstotc"

gmail_host = 'imap.gmail.com'


# select inbox


def get_mail(mail, selected_mails):
    specialChars = "=-_"
    for num in selected_mails[0].split():
        _, data = mail.fetch(num, '(RFC822)')
        # noinspection PyTupleAssignmentBalance
        _, bytes_data = data[0]

        # convert the byte data to message
        email_message = email.message_from_bytes(bytes_data)
        print("\n===========================================")

        # access data

        mail_subject = decode_header(email_message['subject'])

        if type(mail_subject[0][0]) == str:
            mail_subject = mail_subject[0][0]
        else:
            mail_subject = mail_subject[0][0].decode("utf-8")

        mail_from = email_message["from"]
        print("Subject: ", mail_subject)
        print("To:", email_message["to"])
        print("From: ", mail_from)
        print("Date: ", email_message["date"])
        for part in email_message.walk():
            if part.get_content_type() == "text/plain" or part.get_content_type() == "text/html":
                message = part.get_payload(decode=True)
                message = message.decode()
                # Converting HTML to plain Text
                try:
                    if "<!DOCTYPE html>" in str(message):
                        message = html_text.extract_text(message)
                except Exception as e:
                    print("an error has occurred")

                # Removing the links
                if "https" or "http" in message:
                    message = re.sub(r"http\S+", "", message)
                # Removing special characters
                for j in specialChars:
                    message = message.replace(j, "")

                # Printing the message
                print("Message: \n", message)
                # Speak the data
                engine = pyttsx3.init()
                engine.say(
                    f"You got a mail From:{mail_from}. The mail is regarding:{mail_subject}.The mail contains:, {message}")
                engine.runAndWait()
                print("==========================================\n")
                break


def check_mail(mail):
    mail.select("INBOX")

    # select specific mails
    _, selected_mails = mail.search(None, 'UnSeen')

    # total number of mails from specific user
    unread_message = len(selected_mails[0].split())
    print("Total Unread Messages:", unread_message)
    if unread_message > 0:
        get_mail(mail, selected_mails)


def login(email_id, pwd):
    try:
        mail = imaplib.IMAP4_SSL(gmail_host)

        # login
        mail.login(email_id, pwd)
        check_mail(mail)
    except Exception as e:
        print("AN ERROR HAS OCCURRED:", e)


login(username, app_password)
