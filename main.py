import email
import imaplib
import platform
import re
import time
from email.header import decode_header
import text_to_speech
import requests
from html_text import html_text
from plyer import tts
import threading
from kivymd.app import MDApp
from kivy.uix.screenmanager import ScreenManager
from kivy.clock import Clock, mainthread
from kivy.lang.builder import Builder
from kivy.animation import Animation
from kivy.uix.screenmanager import FadeTransition
from kivy.storage.jsonstore import JsonStore
from kivymd.uix.snackbar import Snackbar
from plyer.facades import notification

if platform == 'android':
    from kvdroid.tools.notification import create_notification
    from kvdroid.tools import get_resource


# noinspection PyBroadException
class email_narrator(MDApp):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.log_out = False
        self.store = JsonStore("credentials.json")
        self.screenmanager = None
        self.remember_me = False
        self.EMAIL = ""
        self.PASSWORD = ""
        self.SERVER = ""
        self.mail = None
        self.status = None
        self.paused = False
        self.snackbar = None
        self.exit = False
        self.engine = None
        self.unread_message = 0
        self.internet_connection = False
        self.logo_anim = Animation(pos_hint={"center_x": .5, "center_y": .9}, duration=1, transition='linear')
        self.logo_anim &= Animation(opacity=1, duration=1)
        self.title_anim = Animation(pos_hint={"center_x": .5, "center_y": .8}, duration=1, transition='linear')
        self.title_anim &= Animation(opacity=1, duration=1)
        self.email_textbox_anim = Animation(pos_hint={"center_x": .5, "center_y": .57}, duration=.5,
                                            transition='linear')
        self.email_textbox_anim &= Animation(opacity=1, duration=.5)
        self.pwd_textbox_anim = Animation(pos_hint={"center_x": .5, "center_y": .45}, duration=.5, transition='linear')
        self.pwd_textbox_anim &= Animation(opacity=1, duration=.5)
        self.login_sep_anim = Animation(pos_hint={"center_x": .5, "center_y": .2}, duration=.5, transition='linear')
        self.login_sep_anim &= Animation(opacity=1, duration=.5)
        self.sign_in_text_anim = Animation(pos_hint={"center_x": .5, "center_y": .68}, duration=.5, transition='linear')
        self.sign_in_text_anim &= Animation(opacity=1, duration=.5)
        self.sign_in_btn_anim = Animation(pos_hint={"center_x": .75, "center_y": .3}, duration=.5, transition='linear')
        self.sign_in_btn_anim &= Animation(opacity=1, duration=.5)
        self.google_btn_anim = Animation(pos_hint={"center_x": .25, "center_y": .3}, duration=.5, transition='linear')
        self.google_btn_anim &= Animation(opacity=1, duration=.5)
        self.check_box_anim = Animation(opacity=1, duration=.5)
        self.title_anim.bind(on_complete=self.animation_cascade)

    def on_start(self):
        Clock.schedule_once(self.change_screen, 7)
        url = "http://www.kite.com"
        timeout = 5
        try:
            request = requests.get(url, timeout=timeout)
            print("Connected to the Internet")
            self.internet_connection = True
        except (requests.ConnectionError, requests.Timeout) as exception:
            print("No internet connection.")
            self.internet_connection = False
        pass

    def build(self):
        self.icon = 'appicon.png'
        self.title = "Email-Narrator"
        self.screenmanager = ScreenManager()
        self.screenmanager.add_widget(Builder.load_file("splash.kv"))
        self.screenmanager.add_widget(Builder.load_file("login.kv"))
        self.screenmanager.add_widget(Builder.load_file("mainpage.kv"))
        return self.screenmanager

    def change_screen(self, Nil):
        if self.screenmanager.current == 'splash':
            if self.store.get("credentials")['email'] == "" or self.store.get("credentials")['password'] == "":
                self.screenmanager.transition = FadeTransition()
                self.screenmanager.current = "login"
                self.logo_anim.start(self.root.get_screen("login").ids.appicon)
                self.title_anim.start(self.root.get_screen("login").ids.apptitle)
            else:
                self.screenmanager.transition = FadeTransition()
                self.screenmanager.current = "main"
                self.login(email=self.store.get("credentials")['email'], pwd=self.store.get("credentials")['password'])
        elif self.screenmanager.current == "main" and self.log_out is True:
            self.screenmanager.transition = FadeTransition()
            self.screenmanager.current = "login"
            self.logo_anim.start(self.root.get_screen("login").ids.appicon)
            self.title_anim.start(self.root.get_screen("login").ids.apptitle)

    def animation_cascade(self, x, y):
        self.email_textbox_anim.start(self.root.get_screen('login').ids.email_container)
        self.pwd_textbox_anim.start(self.root.get_screen('login').ids.password_container)
        self.sign_in_text_anim.start(self.root.get_screen('login').ids.signin_text)
        self.login_sep_anim.start(self.root.get_screen('login').ids.login_sep)
        self.sign_in_btn_anim.start(self.root.get_screen('login').ids.signin_btn)
        self.check_box_anim.start(self.root.get_screen('login').ids.auto_log_checkbox)
        self.check_box_anim.start(self.root.get_screen('login').ids.auto_log_text)
        self.google_btn_anim.start(self.root.get_screen('login').ids.google_signin)
        return

    def login(self, email, pwd):
        self.EMAIL = email
        self.PASSWORD = pwd
        self.log_out = False
        if self.internet_connection:

            if email != "":

                if ".com" in email:

                    if self.remember_me is True:
                        self.store.put('credentials', email=email, password=pwd)

                    if "@gmail" in self.EMAIL:
                        self.SERVER = 'imap.gmail.com'

                    elif "@yahoo" in self.EMAIL:
                        self.SERVER = 'imap.mail.yahoo.com'

                    elif "@outlook" in self.EMAIL:
                        self.SERVER = 'imap-mail.outlook.com'

                    else:
                        Snackbar(text="Sorry Email not supported!").open()

                    self.mail = imaplib.IMAP4_SSL(self.SERVER)

                    try:
                        self.status, summary = self.mail.login(self.EMAIL, self.PASSWORD)

                        if self.status == "OK":
                            print("Login Successful")
                            self.root.get_screen('main').ids.user_email.text = str(email)
                            self.screenmanager.current = "main"
                            time.sleep(2)
                            self.th1 = threading.Thread(target=self.check_mail, args=(self.mail,), daemon=True)
                            self.th1.start()
                        else:
                            Snackbar(text="Error Login").open()

                    except (Exception):
                        Snackbar(text="Error logging into Mail").open()
                else:
                    Snackbar(text="Username/Password is wrong").open()
            else:
                Snackbar(text="Please enter the credentials").open()

        else:
            Snackbar(text="No internet connection!").open()

        return self.status, self.mail

    def after_login(self, _email):
        self.root.get_screen('main').ids.user_email.text = _email
        return

    def on_pause(self):
        return True

    def check_mail(self, mail):
        while True:
            if not self.exit and self.log_out is False:
                mail.select("INBOX")

                # select specific mails
                _, selected_mails = mail.search(None, 'UnSeen')

                # total number of mails from specific user
                self.unread_message = len(selected_mails[0].split())
                print("Total Unread Messages:", self.unread_message)
                mail_from, mail_subject = self.mail_from_subject(mail)
                self.update_data()
                if self.unread_message > 0:
                    create_notification(
                        small_icon=get_resource("drawable").ic_launcher,  # app icon
                        channel_id="1", title="You got a Mail",
                        text=f'From: {mail_from}\nSubject: {mail_subject}',
                        ids=1, channel_name=f"ch1",
                    )
                    self.get_mail(mail, selected_mails)
            else:
                break

    def mail_from_subject(self, mail):
        mail_ids = []
        message, mail_from, mail_subject = None, None, None
        status, data = mail.search(None, 'UnSeen')
        for block in data:
            mail_ids += block.split()

        for i in mail_ids:

            status, data = self.mail.fetch(i, '(RFC822)')

            for response_part in data:
                if isinstance(response_part, tuple):
                    message = email.message_from_bytes(response_part[1])
                    mail_from = message['from']

                    mail_subject = decode_header(message['subject'])

                    if type(mail_subject[0][0]) == str:
                        mail_subject = mail_subject[0][0]
                    else:
                        mail_subject = mail_subject[0][0].decode("utf-8")

        return mail_from, mail_subject

    @mainthread
    def update_data(self):
        self.root.get_screen('main').ids.total_msg.text = str(self.unread_message)

    def get_mail(self, mail, selected_mails):
        self.unread_message = len(selected_mails[0].split())
        self.update_data()
        specialChars = "=-_><"
        for num in selected_mails[0].split():
            _, data = mail.fetch(num, '(RFC822)')
            # noinspection PyTupleAssignmentBalance
            _, bytes_data = data[0]

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
                    message = message.decode(errors="replace")
                    # Converting HTML to plain Text
                    try:
                        if "DOCTYPE" in str(message) or "html" in str(message) or "<!DOCTYPE html>" in str(message):
                            message = html_text.extract_text(message)
                    except Exception as e:
                        print("an error has occurred")

                    # Removing the links
                    if "https" or "http" in message:
                        message = re.sub(r"http\S+", "Link", message)
                    # Removing special characters
                    for j in specialChars:
                        message = message.replace(j, "")

                    # Printing the message
                    print("Message: \n", message)
                    # Speak the data
                    msg = f"You got a mail From:{mail_from},, The mail is regarding:{mail_subject},,The mail contains:, {message}"
                    if platform == 'android':
                        tts.speak(msg)
                    else:
                        text_to_speech.speak(msg)
                    print("==========================================\n")
                    break

            if self.unread_message != 0:
                self.unread_message = self.unread_message - 1
                print("Inside for loop:", self.unread_message)
                self.update_data()

    def mute(self):
        if self.root.get_screen('main').ids.mute_btn.icon == 'volume-high':
            self.root.get_screen('main').ids.mute_btn.icon = 'volume-mute'
            print("muted")
            pass
        else:
            print("un muted")
            self.root.get_screen('main').ids.mute_btn.icon = 'volume-high'

    def logoff(self):
        self.log_out = True
        self.change_screen(4)
        # self.store.put('credentials', email="", password="")
        Snackbar(text="Successfully Logged out! ").open()

    def on_stop(self):
        self.exit = True
        if self.engine:
            self.engine.stop()
            self.engine = None


email_narrator().run()
