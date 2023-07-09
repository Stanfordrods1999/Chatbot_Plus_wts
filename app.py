import streamlit as st
st.set_page_config(page_title="Chatbot Plus", page_icon=":fire:",initial_sidebar_state="collapsed",layout="centered")
import Intent_Recognition as ir 
from streamlit_chat import message
import Conversational as cs
import DoFunctionality as df
import folium 
import geocoder
from geopy.geocoders import Nominatim
from streamlit_folium import st_folium, folium_static
import pandas as pd 
import requests

if "Functionality" not in st.session_state:
    st.cache_resource.clear()
    st.session_state.Functionality = False
    st.session_state.initialize = True
    st.session_state.dataset = []
    
app_modes = ['About App','ChatBot','Map']
app_select = st.sidebar.selectbox("Choose the App Mode", app_modes)
if app_select ==  "About App":
    if "paragraph" not in st.session_state:
        file_path = 'text.txt'
        file = open(file_path,"r")
        st.session_state.paragraph = file.read()
        file.close()
    
    with open('index_aboutapp.html','r') as f:
        html_content = f.read()
        
    st.markdown(html_content,unsafe_allow_html=True)
    
elif app_select == "ChatBot":
    chat_placeholder = st.empty()
            
    def on_input_change():
        user_input = st.session_state.user_input
        st.session_state.past.append(user_input)
        x=cs.response(user_input)
        if user_input == 'Functionality()':
            st.session_state.Functionality = True 
            st.session_state.generated.append("Started Functionality")
            st.session_state.user_input = ""
            return ""
        
        if user_input == 'StopFunctionality()':
            st.session_state.Functionality = False
            st.session_state.generated.append("Functionality Stopped")
            st.session_state.user_input = ""
            return ""
                
        if st.session_state.Functionality:
            _,functionality = ir.prediction(user_input)
            st.session_state.initialize = True if functionality == 4 else False
            x = df.switchcase(functionality,user_input)
            
        st.session_state.Check = True
        st.session_state.generated.append(x)
        st.session_state["user_input"] = ""
        
    if "generated" not in st.session_state:
        # st.session_state.setdefault('past',[])
        st.session_state['generated'] = []
        st.session_state['Check'] = False
        x = "Hello, how may I help you?"
        st.session_state['generated'].append(x)
        
    if "past" not in st.session_state:
        st.session_state['past'] = []

    with st.container():
        st.text_input("User Input:", on_change=on_input_change, key = "user_input")
        

    exit_control_var = 1;
    with chat_placeholder.container():
        for i in range(len(st.session_state['generated'])):
            
            if exit_control_var == 1:
                message(st.session_state['generated'][i],key = str(i))
                exit_control_var = 0
                continue
                
            if st.session_state.Check == True:
            #for j in range(len(st.session_state['past'])):
                message(st.session_state['past'][i-1],is_user = True,key = str(i-1)+ "_user_inp")
                
            message(st.session_state['generated'][i],key = str(i),allow_html = True)
        
elif app_select == "Map":
    with open("index_map.html","r") as f:
        html_content = f.read()
    
    st.markdown(html_content,unsafe_allow_html=True)
    #st.session_state.initialize = df.use_map
    if st.session_state.initialize == True:  
        g = geocoder.ip('me')
        geoLoc = Nominatim(user_agent="GetLoc")
        getLoc = geoLoc.reverse(f"{g.lat},{g.lng}")
        url = f"https://api.mapbox.com/geocoding/v5/mapbox.places/restaurant.json?type=poi&proximity={g.lng},{g.lat}&access_token=pk.eyJ1Ijoic3Rhbm55MTIzIiwiYSI6ImNsam9hYjJlbTE2cXIzbnI3M29rcGg1enEifQ.IwJoefqhEqXijARTruWoZA"
        response = requests.get(url)
        data = response.json()
        place_names = [{'place_name':feature['place_name'],'longitude':feature['center'][0],'latitude':feature['center'][1]} for feature in data['features']]
        dataset = pd.DataFrame(place_names)
        dataset.loc[-1] = [getLoc.address,g.lng,g.lat]
        dataset.index = dataset.index + 1
        dataset = dataset.sort_index()
        st.session_state.dataset = dataset

        m = folium.Map(location = [st.session_state.dataset.latitude.mean(), st.session_state.dataset.longitude.mean()],
                    zoom_start=14,control_scale=True)

        for index,row in st.session_state.dataset.iterrows():
            if index == 0:
                folium.Marker([row['latitude'],row['longitude']],
                        popup='<a>'+row['place_name']+'</a>',
                        icon=folium.Icon(color='red',
                                        icon="home",
                                        icon_color="blue",
                                        prefix='fa')).add_to(m)
                continue
                
            folium.Marker([row['latitude'],row['longitude']],
                        popup='<a>'+str(row['place_name'])+'</a>',
                        icon=folium.Icon(color='lightblue',
                                        icon="fa-dollar",
                                        icon_color='black',
                                        prefix='fa')).add_to(m)

        st_data = st_folium(m,width=700)
           
