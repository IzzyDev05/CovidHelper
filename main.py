from http.client import ResponseNotReady
from logging import exception
from urllib import response
import requests
import json
import pyttsx3 #Pythong Text to Speech
import speech_recognition as sr
import re #RegEx search patterns

# The variables received from ParseHub, which was used to scrap the website for the required information 
API_KEY = "tDyuawA_WrcE"
PROJECT_TOKEN = "t88ZsH5x0UTD"
RUN_TOKEN = "tcsgR88_fTy0"

response = requests.get(f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data", params={"api_key": API_KEY})
data = json.loads(response.text)


### GETTING THE DATA
class Data:
    def __init__(self, api_key, project_token):
        self.api_key = api_key
        self.project_token = project_token
        self.params = {
            "api_key": self.api_key
        } 
        self.get_data()

    def get_data(self):
        response = requests.get(f"https://www.parsehub.com/api/v2/projects/{PROJECT_TOKEN}/last_ready_run/data", params={"api_key": API_KEY})
        self.data = json.loads(response.text)

    def get_total_cases(self):
        data = self.data["total"]

        for content in data:
            if (content["name"] == "Coronavirus Cases:"):
                return content["value"]

    def get_total_deaths(self):
        data = self.data["total"]

        for content in data:
            if (content["name"] == "Deaths:"):
                return content["value"]
    
    def get_total_recovered(self):
        data = self.data["total"]

        for content in data:
            if (content["name"] == "Recovered:"):
                return content["value"]

    def get_country_data(self, country):
        data = self.data["country"]

        for content in data:
            if (content["name"].lower() == country.lower()):
                return content

    def get_list_of_countries(self):
        countries = []
        for country in self.data["country"]:
            countries.append(country["name"].lower())
        return countries


### SPEECH RECOGNITION
def speak(text):
    engine = pyttsx3.init()
    engine.say(text)
    engine.runAndWait()

def get_audio():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        r.adjust_for_ambient_noise(source=source, duration=1)
        audio = r.listen(source)
        said = "" # If the Try/Catch messes up, we return a blank string

        try:
            said = r.recognize_google(audio) # The recogonizer is sending the audio to the google assistant, which then returns the text version of what we spoke.
        except Exception as e:
            print("Exception: ", str(e))
    
    return said.lower()


### OUR MAIN FUNCTION WHICH PUTS EVERYTHING TOGETHER
def main():
    print("Hello, welcome to Covid-Help! Ask away! Say 'STOP' to end the program!")
    data = Data(API_KEY, PROJECT_TOKEN)
    END_PHRASE = "stop" # If we hear "quit" anywhere, we end this loop
    country_list = data.get_list_of_countries()

    # These are RegEx search patterns, so the recognizer knows what to look for and what to return for specific phrases. A few for for each
    TOTAL_PATTERNS = {
        re.compile("[\w\s]+ total [\w\s]+ cases"): data.get_total_cases, # [\w\s] means any number of words + abc + any number of words + xyz
        re.compile("[\w\s]+ total cases"): data.get_total_cases,
        re.compile("[\w\s]+ total case"): data.get_total_cases,
        re.compile("[\w\s]+ total [\w\s]+ deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total deaths"): data.get_total_deaths,
        re.compile("[\w\s]+ total death"): data.get_total_deaths,
        re.compile("[\w\s]+ total [\w\s]+ recovered"): data.get_total_recovered,
        re.compile("[\w\s]+ totally recovered"): data.get_total_recovered
    }

    COUNTRY_PATTERNS = {
        re.compile("[\w\s]+ cases [\w\s]+"): lambda country: data.get_country_data(country)["total_cases"],
        re.compile("[\w\s]+ deaths [\w\s]+"): lambda country: data.get_country_data(country)["total_deaths"],
        re.compile("[\w\s]+ recovered [\w\s]+"): lambda country: data.get_country_data(country)["total_recovered"]
    }

    while True:
        print("Listening...")
        text = get_audio()
        print(f"You asked: {text}")
        result = None

        for pattern, func in COUNTRY_PATTERNS.items():
            if (pattern.match(text)):
                words = set(text.split(" ")) # We create a set of our words ("Hey there dude" become {"hey", "there", "dude"}) for ease of checking
                for country in country_list:
                    if (country in words):
                        result = func(country) # Calling the required function of the given country 
                        break

        for pattern, func in TOTAL_PATTERNS.items():
            if (pattern.match(text)):
                result = func() # We defined the functions, but never called them. So, here we are calling whatever function.
                break

        if result:
            print(result)
            speak(result)

        if text.find(END_PHRASE) != -1:
            print("Program stopped!")
            speak("Program stopped!")
            break


### CALLING
main()
