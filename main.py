from Jarvis import JarvisAssistant
import re
import os
import random
import pprint
import datetime
import requests
import sys
import pyjokes
import time
import pyautogui
import pywhatkit
import wolframalpha
from PIL import Image
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtCore import QTimer, QTime, QDate, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QMovie
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from Jarvis.features.gui import Ui_MainWindow
from Jarvis.config import config
import queue
import threading


obj = JarvisAssistant()
speech_queue = queue.Queue()

# ================================ MEMORY ==========================================

GREETINGS = ["hello jarvis", "jarvis", "wake up jarvis", "you there jarvis",
             "time to work jarvis", "hey jarvis", "ok jarvis", "are you there"]
GREETINGS_RES = ["always there for you sir", "i am ready sir",
                 "your wish my command", "how can i help you sir?",
                 "i am online and ready sir"]

EMAIL_DIC = {
    'myself': 'daverbraheems@gmail.com',
    'my official email': 'daverbraheems@gmail.com',
    'my second email': 'daverbraheems@gmail.com',
    'my official mail': 'daverbraheems@gmail.com',
    'my second mail': 'daverbraheems@gmail.com'
}

CALENDAR_STRS = ["what do i have", "do i have plans", "am i busy"]
MUSIC_DIR = os.path.join(os.path.expanduser("~"), "Music")

# ==================================================================================

app_id = config.wolframalpha_id

def speech_worker():
    import pyttsx3
    engine = pyttsx3.init('sapi5')
    engine.setProperty('rate', 175)
    voices = engine.getProperty('voices')
    engine.setProperty('voice', voices[0].id)
    while True:
        text = speech_queue.get()
        if text is None:
            break
        engine.say(text)
        engine.runAndWait()

# Start the speech worker thread once at launch
speech_thread = threading.Thread(target=speech_worker, daemon=True)
speech_thread.start()

def computational_intelligence(question):
    try:
        client = wolframalpha.Client(app_id)
        answer = client.query(question)
        answer = next(answer.results).text
        print(answer)
        return answer
    except:
        return None




def startup(speak_fn):
    speak_fn("Initializing Jarvis")
    speak_fn("Starting all systems and applications")
    speak_fn("Installing and checking all drivers")
    speak_fn("Calibrating and examining all core processors")
    speak_fn("Checking the internet connection")
    speak_fn("Wait a moment sir")
    speak_fn("All drivers are up and running")
    speak_fn("All systems have been activated")
    speak_fn("Now I am online")
    hour = int(datetime.datetime.now().hour)
    if hour >= 0 and hour <= 12:
        speak_fn("Good Morning sir")
    elif hour > 12 and hour < 18:
        speak_fn("Good afternoon sir")
    else:
        speak_fn("Good evening sir")
    c_time = obj.tell_time()
    speak_fn(f"Currently it is {c_time}")
    speak_fn("I am Jarvis. Online and ready sir. Please tell me how may I help you")


# ================================ WORKER THREAD ===================================

class MainThread(QThread):
    # FIX 1: signals to safely update GUI from background thread
    # This fixes the pyttsx3/PyQt5 voice conflict — speech now runs in
    # this thread, never blocking the main GUI thread
    update_log = pyqtSignal(str)
    set_status  = pyqtSignal(str)

    def __init__(self):
        super(MainThread, self).__init__()

    def speak(self, text):
        self.update_log.emit(f"JARVIS: {text}")
        speech_queue.put(text)  # FIX: send to dedicated speech thread

    def run(self):
        self.TaskExecution()

    def TaskExecution(self):
        last_screenshot_path = None
        startup(self.speak)

        while True:
            self.set_status.emit("Listening...")
            command = obj.mic_input()

            # FIX 3: guard against False/None from mic timeout
            if not command or not isinstance(command, str):
                continue

            self.update_log.emit(f"YOU: {command}")
            self.set_status.emit(f"Processing: {command}")

            # ── Date ──────────────────────────────────────────────────────
            if re.search('date', command):
                date = obj.tell_me_date()
                print(date)
                self.speak(date)

            # ── Time ──────────────────────────────────────────────────────
            elif "time" in command:
                time_c = obj.tell_time()
                print(time_c)
                self.speak(f"Sir the time is {time_c}")

            # ── App Launcher ───────────────────────────────────────────────
            elif re.search('launch', command):
                dict_app = {
                    'chrome': 'C:/Program Files/Google/Chrome/Application/chrome'
                }
                app = command.split(' ', 1)[1]
                path = dict_app.get(app)
                if path is None:
                    self.speak('Application path not found')
                else:
                    self.speak('Launching ' + app + ' for you sir!')
                    obj.launch_any_app(path_of_app=path)

            # ── Greetings ─────────────────────────────────────────────────
            elif command in GREETINGS:
                self.speak(random.choice(GREETINGS_RES))

            # ── Open Website ──────────────────────────────────────────────
            elif re.search('open', command):
                domain = command.split(' ')[-1]
                obj.website_opener(domain)
                self.speak(f'Alright sir! Opening {domain}')

            # ── Weather ───────────────────────────────────────────────────
            elif re.search('weather', command):
                city = command.split(' ')[-1]
                weather_res = obj.weather(city=city)
                print(weather_res)
                self.speak(weather_res)

            # ── Wikipedia ─────────────────────────────────────────────────
            elif re.search('tell me about', command):
                topic = command.split(' ')[-1]
                if topic:
                    wiki_res = obj.tell_me(topic)
                    print(wiki_res)
                    self.speak(wiki_res)
                else:
                    self.speak("Sorry sir. I couldn't load your query. Please try again.")

            # ── News ──────────────────────────────────────────────────────
            elif "buzzing" in command or "news" in command or "headlines" in command:
                news_res = obj.news()
                self.speak('Source: The Times Of India')
                self.speak('Todays headlines are..')
                for index, articles in enumerate(news_res):
                    pprint.pprint(articles['title'])
                    self.speak(articles['title'])
                    if index == len(news_res) - 2:
                        break
                self.speak('These were the top headlines. Have a nice day sir!')

            # ── Google Search ─────────────────────────────────────────────
            elif 'search google for' in command:
                obj.search_anything_google(command)
                self.speak("Here are your search results sir.")

            # ── Play Music ────────────────────────────────────────────────
            elif "play music" in command or "hit some music" in command:
                if os.path.exists(MUSIC_DIR):
                    songs = os.listdir(MUSIC_DIR)
                    if songs:
                        for song in songs:
                            os.startfile(os.path.join(MUSIC_DIR, song))
                        self.speak("Playing your music sir.")
                    else:
                        self.speak("Sorry sir, I couldn't find any songs in your music folder.")
                else:
                    self.speak("Sorry sir, the music directory was not found.")

            # ── YouTube ───────────────────────────────────────────────────
            elif 'youtube' in command:
                video = command.replace("play", "").replace("on youtube", "").replace("youtube", "").strip()
                if video:
                    self.speak(f"Okay sir, playing {video} on YouTube")
                    pywhatkit.playonyt(video)
                else:
                    self.speak("What would you like me to play on YouTube sir?")

            # ── Send Email ────────────────────────────────────────────────
            elif "email" in command or "send email" in command:
                sender_email = config.email
                sender_password = config.email_password
                try:
                    self.speak("Whom do you want to email sir?")
                    recipient = obj.mic_input()
                    receiver_email = EMAIL_DIC.get(recipient)
                    if receiver_email:
                        self.speak("What is the subject sir?")
                        subject = obj.mic_input()
                        self.speak("What should I say?")
                        message = obj.mic_input()
                        msg = 'Subject: {}\n\n{}'.format(subject, message)
                        obj.send_mail(sender_email, sender_password, receiver_email, msg)
                        self.speak("Email has been successfully sent")
                        time.sleep(2)
                    else:
                        self.speak("I couldn't find that person's email in my database.")
                except:
                    self.speak("Sorry sir. Couldn't send your mail. Please try again.")

            # ── Calculate ─────────────────────────────────────────────────
            elif "calculate" in command:
                answer = computational_intelligence(command)
                if answer:
                    self.speak(answer)

            # ── What is / Who is ──────────────────────────────────────────
            elif "what is" in command or "who is" in command:
                topic = command.replace("what is", "").replace("who is", "").strip()
                wiki_res = obj.tell_me(topic)
                if wiki_res:
                    print(wiki_res)
                    self.speak(wiki_res)
                else:
                    answer = computational_intelligence(command)
                    if answer:
                        self.speak(answer)

            # ── Google Calendar ───────────────────────────────────────────
            elif any(phrase in command for phrase in CALENDAR_STRS):
                obj.google_calendar_events(command)

            # ── Notes ─────────────────────────────────────────────────────
            elif "make a note" in command or "write this down" in command or "remember this" in command:
                self.speak("What would you like me to write down?")
                note_text = obj.mic_input()
                obj.take_note(note_text)
                self.speak("I've made a note of that.")

            elif "close the note" in command or "close notepad" in command:
                self.speak("Okay sir, closing notepad")
                os.system("taskkill /f /im notepad++.exe")

            # ── Joke ──────────────────────────────────────────────────────
            elif "joke" in command:
                joke = pyjokes.get_joke()
                print(joke)
                self.speak(joke)

            # ── System Info ───────────────────────────────────────────────
            elif "system" in command:
                sys_info = obj.system_info()
                print(sys_info)
                self.speak(sys_info)

            # ── Where Is ─────────────────────────────────────────────────
            elif "where is" in command:
                place = command.split('where is ', 1)[1]
                try:
                    current_loc, target_loc, distance = obj.location(place)
                    city = target_loc.get('city', '')
                    state = target_loc.get('state', '')
                    country = target_loc.get('country', '')
                    time.sleep(1)
                    if city:
                        res = f"{place} is in {state}, {country}. It is {distance} km away."
                    else:
                        res = f"{state} is a state in {country}. It is {distance} km away."
                    print(res)
                    self.speak(res)
                except:
                    self.speak("Sorry sir, I couldn't get the coordinates of that location.")

            # ── IP Address ────────────────────────────────────────────────
            elif "ip address" in command:
                try:
                    ip = requests.get('https://api.ipify.org').text
                    print(ip)
                    self.speak(f"Your IP address is {ip}")
                except:
                    self.speak("Sorry sir, I couldn't fetch your IP address.")

            # ── Switch Window ─────────────────────────────────────────────
            elif "switch the window" in command or "switch window" in command:
                self.speak("Okay sir, switching the window")
                pyautogui.keyDown("alt")
                pyautogui.press("tab")
                time.sleep(1)
                pyautogui.keyUp("alt")

            # ── My Location ───────────────────────────────────────────────
            elif "where i am" in command or "current location" in command or "where am i" in command:
                try:
                    city, state, country = obj.my_location()
                    print(city, state, country)
                    self.speak(f"You are currently in {city}, {state}, {country}.")
                except Exception as e:
                    self.speak("Sorry sir, I couldn't fetch your current location.")

            # ── Screenshot ────────────────────────────────────────────────
            elif "take screenshot" in command or "take a screenshot" in command or "capture the screen" in command:
                self.speak("By what name do you want to save the screenshot?")
                name = obj.mic_input()
                self.speak("Alright sir, taking the screenshot")
                img = pyautogui.screenshot()
                screenshot_filename = f"{name}.png"
                img.save(screenshot_filename)
                last_screenshot_path = screenshot_filename
                self.speak("The screenshot has been successfully captured.")

            elif "show me the screenshot" in command:
                if last_screenshot_path and os.path.exists(last_screenshot_path):
                    try:
                        img = Image.open(last_screenshot_path)
                        img.show()
                        self.speak("Here it is sir.")
                        time.sleep(2)
                    except IOError:
                        self.speak("Sorry sir, I am unable to display the screenshot.")
                else:
                    self.speak("Sorry sir, I don't have a screenshot saved yet.")

            # ── Hide / Show Files ─────────────────────────────────────────
            elif "hide all files" in command or "hide this folder" in command:
                os.system("attrib +h /s /d")
                self.speak("Sir, all the files in this folder are now hidden.")

            elif "visible" in command or "make files visible" in command:
                os.system("attrib -h /s /d")
                self.speak("Sir, all the files in this folder are now visible to everyone.")

            # ── Goodbye ───────────────────────────────────────────────────
            elif "goodbye" in command or "offline" in command or "bye" in command:
                self.speak("Alright sir, going offline. It was nice working with you.")
                sys.exit()

            # ── Fallback ──────────────────────────────────────────────────
            else:
                self.speak("I'm sorry sir, I didn't quite catch that. Could you please repeat?")


startExecution = MainThread()


# ================================ GUI =============================================

class Main(QMainWindow):
    def __init__(self):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # FIX 4: load background GIF once at startup using QMovie
        self.bg_movie = QMovie("Jarvis/utils/images/live_wallpaper.gif")
        self.ui.label.setMovie(self.bg_movie)
        self.bg_movie.start()

        # FIX 5: load top-left GIF at startup
        self.top_movie = QMovie("Jarvis/utils/images/initiating.gif")
        self.ui.label_2.setMovie(self.top_movie)
        self.top_movie.start()

        # FIX 6: connect thread signals to GUI update methods
        startExecution.update_log.connect(self.append_log)
        startExecution.set_status.connect(self.show_status)

        self.ui.pushButton.clicked.connect(self.startTask)
        self.ui.pushButton_2.clicked.connect(self.close)

        # Start clock immediately
        timer = QTimer(self)
        timer.timeout.connect(self.showTime)
        timer.start(1000)
        self.showTime()

    def __del__(self):
        sys.stdout = sys.__stdout__

    def startTask(self):
        # FIX 7: don't reload bg_movie here — it causes white screen
        # Only swap the smaller top GIF to loading animation
        self.top_movie = QMovie("Jarvis/utils/images/loading.gif")
        self.ui.label_2.setMovie(self.top_movie)
        self.top_movie.start()

        # Disable button to prevent double-click
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton.setText("Online")

        startExecution.start()

    def showTime(self):
        current_time = QTime.currentTime()
        current_date = QDate.currentDate()
        self.ui.textBrowser.setText(current_date.toString(Qt.ISODate))
        self.ui.textBrowser_2.setText(current_time.toString('hh:mm:ss'))

    # FIX 8: output window — prints JARVIS responses to textBrowser_3
    def append_log(self, text):
        self.ui.textBrowser_3.append(text)

    # FIX 9: show listening/processing status in the log too
    def show_status(self, text):
        self.ui.textBrowser_3.append(f"[ {text} ]")


# ================================ ENTRY POINT =====================================

app = QApplication(sys.argv)
jarvis = Main()
jarvis.show()
exit(app.exec_())