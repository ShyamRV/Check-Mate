import cv2
import openai
import pyttsx3
import speech_recognition as sr
import webbrowser
import time
import datetime
import pywhatkit

# === INITIAL SETUP ===
# OpenAI setup
openai.api_key = "your-api-key"  # Replace with your OpenAI API key

# Object detection config
thres = 0.45
nms_threshold = 0.2
classFile = "coco.names"
configPath = "ssd_mobilenet_v3_large_coco_2020_01_14.pbtxt"
weightsPath = "frozen_inference_graph.pb"

# Load class names
with open(classFile, "rt") as f:
    classNames = f.read().rstrip("\n").split("\n")

# Load object detection model
net = cv2.dnn_DetectionModel(weightsPath, configPath)
net.setInputSize(320, 320)
net.setInputScale(1.0 / 127.5)
net.setInputMean((127.5, 127.5, 127.5))
net.setInputSwapRB(True)

# TTS engine initialization (outside function for better performance)
engine = pyttsx3.init()
engine.setProperty('rate', 180)


# === CORE FUNCTIONS ===
def say(text):
    print("🤖 Aarryaa:", text)
    engine.say(text)
    engine.runAndWait()


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
                    cv2.putText(img, className.upper(), (box[0] + 10, box[1] + 30),
                                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
                    cv2.putText(img, f'{round(confidence * 100, 2)}%',
                                (box[0] + 10, box[1] + 50), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 0, 0), 2)

    return img, objectInfo


def ai(prompt):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": prompt}]
        )
        result = response['choices'][0]['message']['content']
        say(result)
    except Exception as e:
        say("Sorry, I ran into an issue while processing your request.")
        print("Error with OpenAI:", e)


def takeCommand():
    recognizer = sr.Recognizer()
    with sr.Microphone() as source:
        print("🎤 Listening...")
        recognizer.pause_threshold = 1
        audio = recognizer.listen(source)
    try:
        print("🔍 Recognizing...")
        query = recognizer.recognize_google(audio, language='en-in')
        print(f"👤 You said: {query}")
    except Exception as e:
        say("Sorry, I didn’t get that.")
        return ""
    return query.lower()


# === MAIN LOOP ===
if __name__ == "__main__":
    say("Hi, I am Aarryaa, your receptionist robot assistant.")

    cap = cv2.VideoCapture(0)

    while True:
        success, img = cap.read()
        result, objectInfo = getObjects(img, thres, nms_threshold)
        cv2.imshow("Aarryaa - Smart Reception", result)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break
        elif key == ord('s'):
            say("How can I help you?")
            command = takeCommand()

            if "time" in command:
                now = datetime.datetime.now().strftime("%I:%M %p")
                say(f"The time is {now}")
            elif "open google" in command:
                webbrowser.open("https://www.google.com")
                say("Opening Google")
            elif "open youtube" in command:
                webbrowser.open("https://www.youtube.com")
                say("Opening YouTube")
            elif "play" in command:
                song = command.replace("play", "").strip()
                say(f"Playing {song} on YouTube")
                pywhatkit.playonyt(song)
            elif "where is amity university" in command:
                say("Amity University Bengaluru is located in Choodasandra, Sarjapur, Bangalore.")
            elif "exit" in command or "bye" in command:
                say("Goodbye! Have a nice day.")
                break
            elif command:
                ai(command)

    cap.release()
    cv2.destroyAllWindows()
