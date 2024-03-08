import numpy as np
import LSBSteg
import requests
from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# api for submitting on server
api_base_url = 'http://16.171.171.147:5000'
team_id= 'BFhxJPg'

# api for testing locally
api_base_url = 'http://localhost:8000'
team_id= 'BFhxJPg'

def norm(data,mm=5):
    data[np.isposinf(data)] = 5500
    for i in range(len(data)):
        value = np.percentile(np.array(data[i]), 99)
        data[i][data[i]>=value]=value
        data[i]=data[i]*(mm/value)
        data[i][data[i]>=mm]=mm


def start_model():
    loaded_model = Sequential([
        Conv2D(64, kernel_size=(3, 3), activation='relu', input_shape=(1998, 101, 1)),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(64, kernel_size=(3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(32, kernel_size=(5, 5), activation='relu'),
        Conv2D(32, kernel_size=(7, 7), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(64, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    loaded_model.load_weights('model2_to_submit3_weights.h5')
    return loaded_model

model=start_model()

def call(f1,f2,f3):
    arr= np.array([f1,f2,f3])
    norm(arr)
    predictions = model.predict(np.array(arr))
    mi = 0
    ms = 0.5
    print(predictions)
    for i in range(3):
        if predictions[i]>ms:
            ms=predictions[i]
            mi=i+1
    return mi

def init_eagle(team_id):
    payload = { 'teamId': team_id }
    response = requests.post(api_base_url+"/eagle/start", json=payload , headers={'Content-Type': 'application/json'})
    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
            footprint1 = np.array(data['footprint']['1'])
            footprint2 = np.array(data['footprint']['2'])
            footprint3 = np.array(data['footprint']['3'])
            return footprint1 , footprint2 , footprint3
        except Exception as e:
            print("Error parsing response in init function: ", e)
            end_eagle(team_id)
            return None
    else:
        print("Init Error: ", response.status_code)
        end_eagle(team_id)
        return None

def request_msg(team_id, channel_id):
    payload = {
        'teamId': team_id , 
        'channelId': channel_id
    }
    response = requests.post(api_base_url+"/eagle/request-message", json=payload , headers={'Content-Type': 'application/json'})
    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
            encodedMsg = np.array(data['encodedMsg'])
            return encodedMsg
        except Exception as e:
            print("Error parsing response in request function: ", e)
            end_eagle(team_id)
            return None
    else:
        print("Error in request function: ", response.status_code)
        end_eagle(team_id)
        return None

def skip_msg(team_id):
    payload = {
        'teamId': team_id
    }
    response = requests.post(api_base_url+"/eagle/skip-message", json=payload , headers={'Content-Type': 'application/json'})
    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
            footprint1 = np.array(data['nextFootprint']['1'])
            footprint2 = np.array(data['nextFootprint']['2'])
            footprint3 = np.array(data['nextFootprint']['3'])

            return footprint1 , footprint2 , footprint3
        except Exception as e:
            end_eagle(team_id)
            print("data " , data)
            print("Message is finished or error parsing response in submit function :", e)
            return None
    elif response.status_code == 400:
        print("Finally , There is no more footprints: ", response.content)
        end_eagle(team_id)
        return None
    else:
        print("Error in skip function: ", response.status_code)
        end_eagle(team_id)
        return None

def submit_msg(team_id, decoded_msg):
    payload = {
        'teamId': team_id , 
        'decodedMsg': decoded_msg
    }
    response = requests.post(api_base_url+"/eagle/submit-message", json=payload , headers={'Content-Type': 'application/json'})
    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
            footprint1 = np.array(data['nextFootprint']['1'])
            footprint2 = np.array(data['nextFootprint']['2'])
            footprint3 = np.array(data['nextFootprint']['3'])

            return footprint1 , footprint2 , footprint3
        except Exception as e:
            print("Message is finished or error parsing response in submit function :", e)
            end_eagle(team_id)
            print("data " , data)
            return None
    elif response.status_code == 400:
        print("Finally , There is no more footprints: ", response.content)
        end_eagle(team_id)
        return None
    else:
        print("Error in submit function: ", response.status_code)
        end_eagle(team_id)
        return None

def end_eagle(team_id):
    payload = {
        'teamId': team_id
    }
    response = requests.post(api_base_url+"/eagle/end-game", json=payload , headers={'Content-Type': 'application/json'})
    if response.status_code == 200 or response.status_code == 201:
        print(response.content)
    else:
        print("Error in end function:", response.status_code)

def select_channel(footprint):
    footprint1 , footprint2 , footprint3 = footprint
    res = call(footprint1 , footprint2 , footprint3)
    return res

def submit_eagle_attempt(team_id):
    footprints = init_eagle(team_id)
    if footprints is not None:
        while True:
            channel_id = select_channel(footprints)
            if channel_id != 0:
                encodedmsg = request_msg(team_id, channel_id)
                if encodedmsg is not None:
                    decodedmsg = LSBSteg.decode(encodedmsg)
                    print("Decoded message: ", decodedmsg)
                    footprints = submit_msg(team_id, decodedmsg)
                    if footprints is None:
                        return None
                else:
                    return None
            else:
                footprints = skip_msg(team_id)
                if footprints is None:
                    return None
    else:
        print("Error initializing the game")


submit_eagle_attempt(team_id)