import numpy as np
import unidecode
import string
import random
import time
import math
import numpy
import json
import os
import re
import pickle
import  zipfile
from config import max_token_length,start_word,end_word,batch_size,pcfg_code
from tqdm import tqdm

dict={}
def read_file(filename):
    data=[]
    file = open(filename).readlines()
    for row in file:
        row=unidecode.unidecode(row)
        data.append(row[0:-1])
    return data
def pad(arr,num):
    padding_num=num-len(arr)
    if padding_num>0:
        for i in range(padding_num):
            arr.append(0)
    return arr

def build_samples(usage):
    passwords=read_file('data/pcfg_format_password.csv')
    code=pcfg_code
    letter_format = re.compile(r'[a-zA-z][0-9]+')
    # for i in sorted(code):
    #     print(i,code[i])
    samples=[]
    print('Generating Sample...')
    for i in range(len(passwords)):
        PII_id = i
        password_sample = passwords[i]
        input = []
        last_word = start_word
        letter_list=letter_format.findall(password_sample)
        for letter in letter_list:
            input.append(code[last_word])
            samples.append({'PII_id': PII_id, 'input': list(input), 'output': code[letter]})

            last_word = letter
        input.append(code[last_word])
        samples.append({'PII_id': PII_id, 'input': list(input), 'output': code[end_word]})
    print(samples)
    filename = 'data/pcfg_samples_{}.p'.format(usage)
    with open(filename, 'wb') as f:
        pickle.dump(samples, f)

def encode_PII(usage):
    PII=read_file('data/clean_PII.csv')
    encoding={}
    all_characters = string.printable
    n_characters = len(all_characters)
    code = {}
    for index, letter in enumerate(all_characters):
        code[letter] = index
    code[start_word] = n_characters
    code[end_word] = n_characters + 1


    print('Find out the max size of PII...')
    max_list=[0]*5
    cleaned_PII=[]
    for datum in PII:
            temp=datum.split(',')
            birth=temp[3].split('/')
            if len(birth)>1:
                Y = int(birth[0])
                M = int(birth[1])
                D = int(birth[2])
                temp[3] = '%s%02d%02d' % (Y, M, D)
            for i,pii in enumerate(temp):
                max_list[i]=max(len(pii),max_list[i])
            cleaned_PII.append(temp)
            # maxlen=max(maxlen,len(datum))
    print('The maxsize of PII is ',max_list)
    print(sum(max_list))
    num_batches=int(np.ceil(len(PII)/float(batch_size)))
    print('encoding {} PIIs...'.format(usage))
    for idx in tqdm(range(num_batches)):
        i=idx*batch_size
        length = min(batch_size,len(cleaned_PII)-i)
        for i_batch in range(length):
            PII_data=cleaned_PII[i+i_batch]
            # print(PII_data)
            PII_array=[]
            for j,pii in enumerate(PII_data):
                encode_pii=[]
                for chr in pii:
                    encode_pii.append(code[chr])
                encode_pii=pad(encode_pii,max_list[j])
                PII_array+=encode_pii
            # print(PII_array)
            encoding[i+i_batch]=PII_array

    print(len(encoding))
    filename= 'data/pcfg_encoded_{}_PII.p'.format(usage)
    with open(filename,'wb') as encoded_pickle:
        pickle.dump(encoding,encoded_pickle)

if __name__=='__main__':

    # print(passwords)
    # print(PII)
    build_samples('train')
    encode_PII('train')