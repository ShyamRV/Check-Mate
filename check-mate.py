import cv2
import datetime
import os
import speech_recognition as sr
import pyttsx3
import google.generativeai as genai
import random
import time
import numpy as np

# Replace with your actual Gemini API key
gemini_api_key = "***************************************"
genai.configure(api_key=gemini_api_key)

engine = pyttsx3.init()
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

chatStr = ""

# Initialize Gemini model
gemini_model = genai.GenerativeModel('gemini-pro')

def chat(query):
    global chatStr
    chatStr += f"User: {query}\nCheck-Mate: "
    response = gemini_model.generate_content(chatStr)
    say(response.text)
    chatStr += f"{response.text}\n"
    return response.text

def ai(prompt):
    text = f"Gemini response for Prompt: {prompt} \n*\n\n"
    response = gemini_model.generate_content(prompt)
    text += response.text

    if not os.path.exists("Gemini"):
        os.mkdir("Gemini")
    filename = f"Gemini/{''.join(prompt.split())[:20]}.txt"
    with open(filename, "w") as f:
        f.write(text)

def say(text):
    engine.say(text)
    engine.runAndWait()

def takeCommand():
    r = sr.Recognizer()
    while True:
        with sr.Microphone() as source:
            r.pause_threshold = 2
            print("Listening...")
            audio = r.listen(source, timeout=20)
            try:
                query = r.recognize_google(audio, language="en-in")
                print(f"User said: {query}")
                return query
            except sr.UnknownValueError:
                say("Sorry, I did not hear your request. Please repeat.")
            except sr.RequestError as e:
                say("Could not request results from Google Speech Recognition service")
                return ""

def find_room_number(x):
    room = ["aiml", "cse", "vc", "hod", "engineering staff room", "computer lab", "library", "registrard"]
    room_numbers = [207, 206, 105, 201, 202, 203, 208, 199]
    x_lower = x.lower()
    for room_name, room_number in zip(room, room_numbers):
        if room_name in x_lower:
            return f"It is on the second floor. Room number {room_number}"
    say("Room not found.")
    return "Room not found."

def main():
    global chatStr
    timestamp = int(time.strftime('%H'))
    time_now = timestamp

    greetings = {
        "morning": ["Good Morning! Welcome to Amity University Bangalore"],
        "afternoon": ["Good Afternoon! Welcome to Amity University Bangalore"],
        "evening": ["Good Evening! Welcome to Amity University Bangalore"]
    }

    cap = cv2.VideoCapture(0)
    cap.set(3, 640)
    cap.set(4, 480)

    while True:
        success, img = cap.read()
        result, objectInfo = getObjects(img, 0.45, 0.2)

        if objectInfo:
            if time_now < 12:
                say(random.choice(greetings["morning"]))
            elif time_now < 18:
                say(random.choice(greetings["afternoon"]))
            else:
                say(random.choice(greetings["evening"]))

            say("Check-Mate under charge. Let's complete the formalities. Please fill the required details in the register.")
            say("Hope you have filled your details in the register.")
            say("How can I assist you today?")
            break
        cv2.imshow("Output", img)
        cv2.waitKey(1)

    while True:
        query = takeCommand().lower()
        if "exit" in query or "quit" in query:
            say("Goodbye!")
            break
        elif "the time" in query:
            say(datetime.datetime.now().strftime("%H:%M:%S"))
        elif "using artificial intelligence" in query:
            ai(prompt=query)
        elif "reset chat" in query:
            chatStr = ""
            say("Chat reset")
        elif "how are you" in query:
            say(random.choice(["I'm doing great, thank you.", "I'm happy to assist you!"]))
        elif "your purpose" in query:
            say("I am a humanoid receptionist robot created by the team Roboverse for Amity University Bengaluru.")
        elif "creator" in query or "father" in query:
            say("I was created by team Roboverse: Shyamji Pandey, Harshul Singh, Utkarsh Mishra, and Sumith Kumar Gupta.")
        elif "birthday" in query:
            say("I was created on 2nd February 2024 by the team Roboverse.")
        elif "introduce yourself" in query:
            say("My name is Check-Mate, an AI-powered receptionist robot.")
        elif "shutdown" in query:
            say("Shutting down")
            os.system("shutdown /s /t 1")
        elif any(room in query for room in ["aiml", "cse", "vc", "hod", "engineering staff room", "computer lab", "library", "registrard"]):
            room_info = find_room_number(query)
            say(room_info)
        elif "thank you" in query:
            say("You're welcome! Goodbye!")
            break
        elif "located" in query:
            say("Located near Doddaballapura DC office, Chapparaddkallu, Bengaluru rural district, Karnataka.")
        elif "head of department" in query:
            say("Dr. Swarnalatha K S is the head of B.Tech.")
        elif "chancellor" in query:
            say("Dr. P Sali is the Chancellor of Amity University Bengaluru.")
        elif "vice chancellor" in query:
            say("Dr. Sudhakar is the Vice Chancellor of Amity University Bengaluru.")
        elif "courses" in query:
            say("B.Tech CSE, AIML for UG. MBA, MSc Cyber Security, MSc Data Science, MCA for PG.")
        elif "about amity" in query:
            say("Amity University Bengaluru is a private university founded in 2023.")
        else:
            print("Chatting...")
            chat(query)

# Object Detection Setup
classNames = []
classFile = "C:\\Users\\S S MISHRA\\OneDrive\\Desktop\\Object_Detection_Files\\coco.names"
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

configPath = "C:\\Users\\S S MISHRA\\OneDrive\\Desktop\\Object_Detection_Files\\ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "C:\\Users\\S S MISHRA\\OneDrive\\Desktop\\Object_Detection_Files\\frozen_inference_graph.pb"

net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

def getObjects(img, thres, nms, draw=True, objects=[]):
    classIds, confs, bbox = net.detect(img, confThreshold=thres, nmsThreshold=nms)
    if len(objects) == 0:
        objects = classNames
    objectInfo = []
    if len(classIds) != 0:
        for classId, confidence, box in zip(classIds.flatten(), confs.flatten(), bbox):
            className = classNames[classId - 1]
            if className in objects:
                objectInfo.append([box, className])
                if draw:
                    cv2.rectangle(img, box, color=(0, 255, 0), thickness=2)
                    cv2.putText(img, className.upper(), (box[0]+10, box[1]+30),
                                cv2.FONT_HERSHEY_COMPLEX, 1, (0, 255, 0), 2)
    return img, objectInfo

if __name__ == "__main__":
    main()