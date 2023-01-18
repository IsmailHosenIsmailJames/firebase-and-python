# Read all images and store in a folder. Folder name is ./img/
import os
import cv2
import face_recognition
import pickle
import requests
import firebase_admin
from firebase_admin import credentials,firestore

# initialize firebase server
cd = credentials.Certificate("tpi-student-database-15c14-firebase-adminsdk-fkfla-12512f7f93.json")
firebase_admin.initialize_app(cd)
datab = firestore.client()
usersref = datab.collection(u'all user')
docs = usersref.stream()

# downloade all image from server and store with proper data
try: os.mkdir('img')
except: print("No need to create folder: img")
for doc in docs:
    info = doc.to_dict()
    tag = info['tag']
    if(tag != 'student'): continue
    name = info['name']
    roll = info['roll']
    reg = info['reg']
    semester = info['semester']
    shift = info['shift']
    group = info['group']
    deperment = info['deperment']
    img_url = info['img']
    response = requests.get(img_url, stream= True)
    if response.status_code == 200:
        print("Downloade Successfull :", doc.id)
        fp = open(f'img/shift {shift}_{deperment}_semester {semester}_{group}_{roll}_{reg}_{name}_{doc.id}.jpg', 'wb')
        fp.write(response.content)
        fp.close()
    else:
        print(f'fail to receved data : shift {shift}_{deperment}_semester {semester}_{group}_{roll}_{reg}_{name}_{doc.id}.jpg')

# Create a nasted Database folder where we will store images
path = 'img'
list_of_image_name = os.listdir(path)
for image in list_of_image_name:
    current_image = cv2.imread(f'{path}/{image}')
    data = image.split('_')
    current_path = f'img data/{data[0]}/{data[1]}/{data[2]}/{data[3]}/'
    try: os.makedirs(current_path)
    except: print('Already exits. No need to create folder :', current_path)
    cv2.imwrite(f'{current_path}/{data[4]}_{data[5]}_{data[6]}_{data[7]}', current_image)

# make face recognition and strore in a folder Database
path = 'img data'
try: os.mkdir(path)
except: print("No need to create folder : img data/")
list_shift = os.listdir(path)
cause_error = False
for shift in list_shift:
    list_deperment = os.listdir(f'{path}/{shift}')
    for deperment in list_deperment:
        list_semester = os.listdir(f'{path}/{shift}/{deperment}')
        for semester in list_semester:
            list_of_group = os.listdir(f'{path}/{shift}/{deperment}/{semester}')
            for group in list_of_group:
                list_of_image = os.listdir(f'{path}/{shift}/{deperment}/{semester}/{group}')
                list_of_encoding = []
                for Current_image_name in list_of_image:
                    working_path = f'{path}/{shift}/{deperment}/{semester}/{group}/{Current_image_name}'
                    Current_image_file = cv2.imread(working_path)
                    encode = face_recognition.face_encodings(Current_image_file)
                    if(len(encode) != 1):
                        error_path = working_path.replace('/', '_')
                        try: os.mkdir('error')
                        except: print("No need to create folder : error/", )
                        cv2.imwrite(f"error/{error_path}", Current_image_file)
                        print("Contain", len(encode) ,  "face in iamge: \n", working_path)
                        cause_error = True
                    else:
                        list_of_encoding.append(encode)
                savePath = f'face data/{shift}/{deperment}/{semester}/{group}/'
                try: os.makedirs(savePath)
                except : print("No need to create Folder:", savePath)
                file = open(f'{savePath}/facedata.pkl', 'wb')
                pickle.dump(file=file, obj=list_of_encoding)
                file.close()
# Done all task.
if cause_error: print("Cause error. to cheak error please go to /error/ folder.")
else: print("Successfull. No error cause.")
