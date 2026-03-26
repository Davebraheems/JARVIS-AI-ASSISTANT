import speech_recognition as sr

r = sr.Recognizer()

# FIX 1: Lower sensitivity so quiet voices are picked up
r.energy_threshold = 200
r.dynamic_energy_threshold = False
r.pause_threshold = 0.8  # wait a bit longer before cutting off

print("Microphone devices available:")
for i, mic in enumerate(sr.Microphone.list_microphone_names()):
    print(f"  {i}: {mic}")

print("\nTesting mic input... speak something!")

# FIX 2: Use device_index=1 (your confirmed working Realtek mic)
with sr.Microphone(device_index=1) as source:
    print("Calibrating for background noise...")
    r.adjust_for_ambient_noise(source, duration=2)  # FIX 3: longer calibration
    print(f"Energy threshold set to: {r.energy_threshold}")
    print("Listening... speak now!")
    audio = r.listen(source, timeout=10, phrase_time_limit=10)  # FIX 4: more time

print("Recognizing...")
try:
    text = r.recognize_google(audio, language="en-US")  # FIX 5: explicit language
    print(f"You said: {text}")
except sr.UnknownValueError:
    print("Could not understand audio — try speaking louder or closer to the mic")
except sr.RequestError as e:
    print(f"Google API error: {e} — check your internet connection")



# import speech_recognition as sr

# r = sr.Recognizer()

# print("Microphone devices available:")
# for i, mic in enumerate(sr.Microphone.list_microphone_names()):
#     print(f"  {i}: {mic}")

# print("\nTesting mic input... speak something!")
# with sr.Microphone() as source:
#     r.adjust_for_ambient_noise(source, duration=1)
#     print("Listening...")
#     audio = r.listen(source, timeout=5)

# print("Recognizing...")
# text = r.recognize_google(audio)
# print(f"You said: {text}")

