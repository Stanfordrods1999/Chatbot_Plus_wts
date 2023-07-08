"""import urllib.parse
import urllib.request
import re
import yake

kw_extractor = yake.KeywordExtractor(top=3, stopwords="Play")

def get_video_url(extracted:str) -> str:
    encoded_query = urllib.parse.quote(extracted)
    url = f"https://www.youtube.com/results?search_query={encoded_query}"

    html = urllib.request.urlopen(url).read().decode('utf-8')

    # Extract video ID
    video_ids = re.findall(r"watch\?v=(\S{11})", html)
    first_video_id = video_ids[0]
    
    src = "https://www.youtube.com/embed/" + video_ids[0]
    
    return src

keywords = kw_extractor.extract_keywords("Play Sams Smith too good at goodbyes")

def Do_Append(keywords, text):
    new_word = ""
    if len(keywords) == 0:
        return text
    else:
        for kw, v in keywords:  # Assuming keywords is a dictionary
            new_word += kw +" "
        return new_word

def extract_keywords_and_url(user_input:str)->str:
    keywords = kw_extractor.extract_keywords(user_input)
    sentence = Do_Append(keywords,user_input)
    words = sentence.split()  # Split the sentence into a list of words
    unique_words = list(set(words))  # Remove duplicates using a set
    result = ' '.join(unique_words)  # Join the unique words back into a string
    link = get_video_url(result)
    return link

def SwitchCase(functionality,user_input):
    if functionality == 0:
        link = extract_keywords_and_url(user_input)
        string_url = f'''<iframe width="400" height="215" src= "{link}" title="YouTube video player" frameborder="0" allow="accelerometer; encrypted-media;"></iframe>'''
        return string_url """

import urllib.parse
import urllib.request
import re
import yake
import nltk
import geonamescache
from geopy.geocoders import Nominatim 
from spacy import load
from bs4 import BeautifulSoup
import requests
import pandas as pd 

use_map = False
class VideoExtractor:
    def __init__(self):
        self.kw_extractor = yake.KeywordExtractor(top=3, stopwords="Play")  # Initialize your keyword extractor here

    def get_video_url(self, extracted: str) -> str:
        encoded_query = urllib.parse.quote(extracted)
        url = f"https://www.youtube.com/results?search_query={encoded_query}"

        html = urllib.request.urlopen(url).read().decode('utf-8')

        # Extract video ID
        video_ids = re.findall(r"watch\?v=(\S{11})", html)
        #first_video_id = video_ids[0]

        src = "https://www.youtube.com/embed/" + video_ids[0]

        return src

    def do_append(self, keywords, text):
        new_word = ""
        if len(keywords) == 0:
            return text
        else:
            for kw, v in keywords:  # Assuming keywords is a dictionary
                new_word += kw + " "
            return new_word

    def extract_keywords_and_url(self, user_input: str) -> str:
        keywords = self.kw_extractor.extract_keywords(user_input)
        sentence = self.do_append(keywords, user_input)
        words = sentence.split()  # Split the sentence into a list of words
        unique_words = list(set(words))  # Remove duplicates using a set
        result = ' '.join(unique_words)  # Join the unique words back into a string
        link = self.get_video_url(result)
        return link

        
class WeatherExtractor:
    def __init__(self):
        self.gc = geonamescache.GeonamesCache()
        self.cities = self.gc.get_cities()
        self.nlp = load("en_core_web_sm")
        self.relevant_cities = []
        
    def gen_dict_extract(self,var, key):
        if isinstance(var, dict):
            for k, v in var.items():
                if k == key:
                    yield v
                if isinstance(v, (dict, list)):
                    yield from self.gen_dict_extract(v, key)
        elif isinstance(var, list):
            for d in var:
                yield from self.gen_dict_extract(d, key)
                        
    def get_relevant_cities(self,sentence):
        self.cities = self.gen_dict_extract(self.cities,'name')
        print(self.cities)
        doc = self.nlp(sentence)
        for ent in doc.ents:
            if ent.label_ == 'GPE':
                if ent.text in self.cities:
                    self.relevant_cities.append(ent.text)
                       
    def get_weather(self,sentence):
        result_string = None
        self.get_relevant_cities(sentence)
        for city in self.relevant_cities:
            print(city)
            geolocater = Nominatim(user_agent="MyApp")
            getLocation = geolocater.geocode(city)
            url = f"https://api.open-meteo.com/v1/forecast?latitude={getLocation.latitude}&longitude={getLocation.longitude}&hourly=temperature_2m,relativehumidity_2m,precipitation_probability,precipitation,rain,showers,weathercode"
            response = requests.get(url=url)
            data = response.json()
            df = pd.DataFrame(data['hourly'])
            df['time'] = pd.DataFrame(df['time'])
            df = df.set_index('time')
            first_row = df.iloc[0] 
            units = data['hourly_units']
            result_string = f"City is: {city}" + " \n "
            for index,values in first_row.items():
                result_string += f"{index} is :-" + str(values) + units[index] + " \n "
            # Printing the result string
        return result_string if result_string is not None else "Retrieval failed"
    
class MapRestaurantExtractor:
    def __init__(self) -> None:
        self.temp = True
        

def switchcase(functionality, user_input):
    
    if functionality == 0:
        extractor = VideoExtractor()
        link = extractor.extract_keywords_and_url(user_input)
        string_url = f'''<iframe width="400" height="215" src="{link}" title="YouTube video player" frameborder="0" allow="accelerometer; encrypted-media;"></iframe>'''
        return string_url
    
    if functionality == 4:
        #extractor = MapRestaurantExtractor()
        return "Please check the Nearest Restaurants in the Map"
    
    if functionality == 5:
        extractor = WeatherExtractor()
        return extractor.get_weather(user_input)