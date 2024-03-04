# Load the entire model
import numpy as np


# Load only the weights into a new model


from keras.models import Sequential
from keras.layers import Conv2D, MaxPooling2D, Flatten, Dense

# Define a ModelCheckpoint callback

def start_model():
    loaded_model = Sequential([
        Conv2D(64, kernel_size=(3, 3), activation='relu', input_shape=(1998, 101, 1)),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(64, kernel_size=(3, 3), activation='relu'),
        MaxPooling2D(pool_size=(2, 2)),
        Conv2D(32, kernel_size=(5, 5), activation='relu'),
        Conv2D(32, kernel_size=(7, 7), activation='relu'),
        Flatten(),
        Dense(128, activation='relu'),
        Dense(64, activation='relu'),
        Dense(1, activation='sigmoid')
    ])
    loaded_model.load_weights('model_2_weights.h5')
    return loaded_model


def con(d):
    mx = 0
    nonsec = 0
    currentmax=0
    for i in range (1998):
        num=0
        for j in range (50):
            if d[i][j] > 1 :
                num+=1
            else :num-=1
            if num > 2:
                currentmax+=1
                mx = max(currentmax,mx)
                nonsec=0
                break
            elif num < -10 or j == 49:
                nonsec-=1
                if nonsec==-3:
                    currentmax=0
                    nonsec=0
                break

    return mx


model = start_model()

def call(f1,f2,f3):
    arr=np.array([f1,f2,f3])
    f1[np.isinf(f1)] = 65500
    f2[np.isinf(f2)] = 65500
    f2[np.isinf(f3)] = 65500
    f1 = (f1 / 65500) * 255
    f2 = (f2 / 65500) * 255
    f3 = (f3 / 65500) * 255
    predictions = model.predict(np.array([f1,f2,f3]))
    mi = 0
    ms = 0.5
    for i in range(3):
        if predictions[i]>ms:
            if con(arr[i])>50:
                ms=predictions[i]
                mi=i+1
    return mi




fake_data = np.load('fake.npz')
real_data = np.load('real.npz')
fx,rx,fy,ry=fake_data['x'],real_data['x'],fake_data['y'],real_data['y']

predictions = model.predict(rx)
predictions[predictions>0.5] = 1
predictions[predictions<=0.5] = 0

print(sum(predictions) / len(predictions))

print(call(fx[740],fx[632],fx[599]))