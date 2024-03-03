import numpy as np
import LSBSteg
import requests
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# api_base_url = 'http://3.70.97.142:5000'
# team_id= 'BFhxJPg'

api_base_url = 'http://127.0.0.1:8000'
team_id= 'abcdefghi'

def make_prediction(model_path, data_point):
#     # Load the trained model from the file
#     model = joblib.load(model_path)
#     # Make predictions for the input data point
#     prediction = model.predict(data_point)
#     # Return the prediction (0 or 1)
#     return prediction[0]
    pass

def init_eagle(team_id):
    '''
    In this fucntion you need to hit to the endpoint to start the game as an eagle with your team id.
    If a sucessful response is returned, you will recive back the first footprints.
    '''
    payload = {
        'teamId': team_id
    }
    response = requests.post(api_base_url+"/eagle/start", json=payload , headers={'Content-Type': 'application/json'})
    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()

            # Extract footprints
            footprint1 = np.array(data['footprint']['1'])
            footprint2 = np.array(data['footprint']['2'])
            footprint3 = np.array(data['footprint']['3'])
            print("footprint1 shape: " , footprint1.shape)
            return footprint1 , footprint2 , footprint3
        except Exception as e:
            print("Error parsing response in init function :", e)
            end_eagle()
            return None
    else:
        print("Init Error:", response.status_code)
        end_eagle()
        return None

def request_msg(team_id, channel_id):
    '''
    If you decide to listen to any of the 3 channels then you need to hit the end point of selecting a channel to hear on (1,2 or 3)
    '''
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
            print("Error parsing response in request function :", e)
            end_eagle()
            return None
    else:
        print("Error in request function:", response.status_code)
        end_eagle()
        return None

def skip_msg(team_id):
    '''
    If you decide to NOT listen to ANY of the 3 channels then you need to hit the end point skipping the message.
    If sucessful request to the end point , you will expect to have back new footprints IF ANY.
    '''
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
            print("data " , data)
            print("Message is finished or error parsing response in submit function :", e)
            end_eagle()
            return None
    else:
        print("Error in Skipping function:", response.status_code)
        end_eagle()
        return None

def submit_msg(team_id, decoded_msg):
    '''
    In this function you are expected to:
        1. Decode the message you requested previously
        2. call the api end point to send your decoded message  
    If sucessful request to the end point , you will expect to have back new footprints IF ANY.
    '''
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
            print("data " , data)
            print("Message is finished or error parsing response in submit function :", e)
            end_eagle()
            return None
    else:
        # Print an error message if the request was not successful
        print("Error in submit function:", response.status_code)
        end_eagle()
        return None

def end_eagle(team_id):
    '''
    Use this function to call the api end point of ending the eagle  game.
    Note that:
    1. Not calling this fucntion will cost you in the scoring function
    '''
    payload = {
        'teamId': team_id
    }
    response = requests.post(api_base_url+"/eagle/end-game", json=payload , headers={'Content-Type': 'application/json'})
    if response.status_code == 200 or response.status_code == 201:
        try:
            data = response.json()
            print("end function " , data)
        except Exception as e:
            print("Error parsing response in end function :", e)
    else:
        print("End error:", response.status_code)

def select_channel(footprint): # return number of selected channel
    '''
    According to the footprint you recieved (one footprint per channel)
    you need to decide if you want to listen to any of the 3 channels or just skip this message.
    Your goal is to try to catch all the real messages and skip the fake and the empty ones.
    Refer to the documentation of the Footprints to know more what the footprints represent to guide you in your approach.        
    '''
    footprint1 , footprint2 , footprint3 = footprint
    # Use the trained model to make predictions
    res1 = make_prediction('trained_model.pkl', footprint1)
    res2 = make_prediction('trained_model.pkl', footprint2)
    res3 = make_prediction('trained_model.pkl', footprint3)
    if res1 == 1:
        return 1 # number of channel
    elif res2 == 1:
        return 2
    elif res3 == 1:
        return 3
    else:
        return 0

def submit_eagle_attempt(team_id):
    '''
     Call this function to start playing as an eagle. 
     You should submit with your own team id that was sent to you in the email.
     Remeber you have up to 15 Submissions as an Eagle In phase1.
     In this function you should:
        1. Initialize the game as fox 
        2. Solve the footprints to know which channel to listen on if any.
        3. Select a channel to hear on OR send skip request.
        4. Submit your answer in case you listened on any channel
        5. End the Game
    '''
    footprints = init_eagle(team_id)
    if footprints is not None:
        while True:
            channel_id = select_channel(footprints)
            if channel_id is not None:
                encodedmsg = request_msg(team_id, channel_id)
                if encodedmsg is not None:
                    decodedmsg = LSBSteg.decode(encodedmsg)
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

def start_model():
    loaded_model = Sequential([
        Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(1998, 101, 1)),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(64, kernel_size=(3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(64, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    loaded_model.load_weights('model_weights.h5')
    return loaded_model



submit_eagle_attempt(team_id)
