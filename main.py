import speech_recognition as sr
import webbrowser
import pyttsx3
import musicLibrary
import requests
from gtts import gTTS
import pygame
import os
import threading

# Initialize the recognizer and speech engine
recognizer = sr.Recognizer()
engine = pyttsx3.init()
newsapi = "648677dc02254c57afc660a42858d6f6"

def speak(text):
    # Convert text to speech using Google Text-to-Speech
    tts = gTTS(text)
    tts.save('temp.mp3')

    # Initialize Pygame mixer
    pygame.mixer.init()

    # Load and play the MP3 file
    pygame.mixer.music.load('temp.mp3')
    pygame.mixer.music.play()

    # Wait until the speech finishes
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

    # Cleanup after playing
    pygame.mixer.music.unload()
    os.remove("temp.mp3")
    pygame.mixer.quit()

def processCommand(c):
    c = c.lower()
    print(f"Recognized Command: {c}")  # Display the recognized command in the terminal

    if "exit" in c:
        speak("Goodbye!")
        os._exit(0)  # Exit the program
    
    elif "open google" in c:
        webbrowser.open("https://google.com")
    elif "open facebook" in c:
        webbrowser.open("https://facebook.com")
    elif "open youtube" in c:
        webbrowser.open("https://youtube.com")
    elif "open linkedin" in c:
        webbrowser.open("https://linkedin.com")
    elif "open spotify" in c:
        webbrowser.open("https://spotify.com")
    elif c.startswith("play"):
        song = c.split(" ")[1]
        link = musicLibrary.music.get(song, None)
        if link:
            webbrowser.open(link)
        else:
            speak("Sorry, I couldn't find the song.")
    elif "news" in c:
        r = requests.get(f"https://newsapi.org/v2/top-headlines?country=in&apiKey={newsapi}")
        if r.status_code == 200:
            data = r.json()
            articles = data.get('articles', [])
            for article in articles[:5]:  # Limit to the first 5 headlines
                speak(article['title'])
        else:
            speak("Sorry, I couldn't fetch the news.")

def listen_for_command():
    try:
        with sr.Microphone() as source:
            print("Listening for your command...")
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=5)
            command = recognizer.recognize_google(audio)
            return command.lower()
    except sr.UnknownValueError:
        print("Sorry, I didn't catch that. Could you repeat?")
        return None
    except sr.RequestError as e:
        print(f"Could not request results; {e}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def voice_input_loop():
    while True:
        try:
            with sr.Microphone() as source:
                print("Listening for wake word 'Jarvis'...")
                recognizer.adjust_for_ambient_noise(source)
                audio = recognizer.listen(source, timeout=5, phrase_time_limit=2)

            # Recognize the wake word
            word = recognizer.recognize_google(audio).lower()
            if "jarvis" in word:
                speak("Yes, how can I help you?")
                
                # Listen for command after wake word
                print("Waiting for your command...")
                command = listen_for_command()
                if command:
                    processCommand(command)

        except sr.WaitTimeoutError:
            print("Listening timed out, please try again.")
        except sr.UnknownValueError:
            print("Sorry, I didn't catch that. Could you repeat?")
        except sr.RequestError as e:
            print(f"Could not request results; {e}")
        except Exception as e:
            print(f"Error: {e}")

def keyboard_input_loop():
    while True:
        command = input("Enter your command (or leave blank to continue voice mode): ").strip()
        if command:
            processCommand(command)

if __name__ == "__main__":
    speak("Initializing Jarvis...")

    # Run the voice input loop in a separate thread
    voice_thread = threading.Thread(target=voice_input_loop)
    voice_thread.daemon = True
    voice_thread.start()

    # Keyboard input loop in the main thread
    keyboard_input_loop()
