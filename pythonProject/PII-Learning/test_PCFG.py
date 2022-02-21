import argparse
import keras
import random
import unidecode
import numpy as np
import tensorflow as tf
from keras.callbacks import ModelCheckpoint, EarlyStopping, ReduceLROnPlateau
# from keras.utils import multi_gpu_model
from config import patience, n_epochs, num_train_samples, num_valid_samples, batch_size
from config import code,pcfg_code,pcfg_decode,max_token_length,PII_size
from model import build_model, Model
from data_generator import *
import matplotlib.pyplot as plt


def read_file(filename):
    data=[]
    file = open(filename).readlines()
    for row in file:
        row=unidecode.unidecode(row)
        data.append(row[0:-1])
    return data

def ensure_folder(folder):
    if not os.path.exists(folder):
        os.makedirs(folder)

def encode_PII(PII):
    PII_array=[]
    for ch in PII:
        PII_array.append(code[ch])
    return PII_array

def pad(encoded_arr,pad_size):
    padding_num = pad_size - len(encoded_arr)
    for i in range(padding_num):
        encoded_arr.append(0)
    return  encoded_arr

def get_pred(prediction):
    max_p = 0
    max_index = 0
    for i, p in enumerate(prediction[0]):
        if p > max_p:
            max_p = p
            max_index = i
    return pcfg_decode[max_index]
#输出预测概率表
def read_pred(prediction):
    note=[]
    for i,p in enumerate(prediction[0]):
        note.append([pcfg_decode[i],p])
    note=sorted(note,key=lambda k:k[-1],reverse=True)
    # print(note[:11])
    return note
if __name__=='__main__':
    model=build_model()

    model.load_weights('models/PCFG/1.0.1_Add_Norm_47.5%.hdf5')
    PIIs = read_file('data/clean_PII.csv')
    passwords=read_file('data/pcfg_format_password.csv')
    input_PIIs=[]
    start_password=[pcfg_code[start_word]]
    start_password=pad(start_password,max_token_length)
    input_passwords=[]
    for PII in PIIs:
        encoded_PII=encode_PII(PII)
        encoded_PII=pad(encoded_PII,PII_size)
        input_PIIs.append(encoded_PII)
    for _ in range(len(PIIs)):
        input_passwords.append(start_password)


    correct_num=0
    for i in range(len(input_PIIs)):
        # print(i)
        # print("-----------------")
        # print("PII",PIIs[i])
        # print("passwords: ",passwords[i])
        input_PII=[input_PIIs[i]]
        input_password=[input_passwords[i]]
        input_PII=np.array(input_PII)
        input_password=np.array(input_password)
        cnt=1
        pred_password=""
        while True:
            prediction=model.predict([input_PII,input_password])
            # print(prediction)
            pred=get_pred(prediction)
            read_pred(prediction)
            # print(pred)
            if pred==end_word:
                break
            if cnt>=18:
                break
            pred_password += pred
            input_password[0][cnt]=pcfg_code[pred]
            cnt+=1
        if passwords[i]==pred_password:
            correct_num+=1

        if not pred_password=='L6':
            print(passwords[i],'  ',pred_password)
        # print("----------------")
    print(correct_num)
"""
    model = Model(50)
    model.load("path") #load from the selected path
    model(input)
"""
    # PII=""
    # password=""
    # for item in x1[1]:
    #     PII+=decode[item]
    # print("PII: ",PII)
    # for item in x2[1]:
    #     password+=decode[item]
    # print("password: ",password)
