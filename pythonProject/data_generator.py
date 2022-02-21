import pickle

import keras
import numpy as np
from keras.preprocessing import sequence
from tensorflow.keras.utils import Sequence,to_categorical
import string
from config import batch_size, max_token_length,PII_size
from config import start_word,end_word
from pre_process import read_file
class DataGenSequence(Sequence):
    def __init__(self,usage):
        self.usage = usage
        all_characters = string.printable
        n_characters = len(all_characters)
        code = {}
        for index, letter in enumerate(all_characters):
            code[letter] = index
        code[start_word] = n_characters
        code[end_word] = n_characters + 1

        filename = '/data/encoded_{}_PII.p'.format(usage)
        self.PII_encoding=pickle.load(open(filename,'rb'))

        if usage == 'train':
            samples_path = '/data/samples_train.p'

        samples = pickle.load(open(samples_path,'rb'))
        self.samples = samples
        np.random.shuffle(self.samples)
    def __len__(self):
        return int(np.ceil(len(self.samples)/float(batch_size)))

    def __getitem__(self,idx):
        i=idx*batch_size

        length=min(batch_size,(len(self.samples)-i))
        batch_PII_input = np.empty((length,PII_size),dtype=np.float32)
        batch_y=np.empty((length,len(code)),dtype=np.int32)
        password_input=[]

        for i_batch in range(length):
            sample = self.samples[i+i_batch]
            PII_id = sample['PII_id']
            PII_input=np.array(self.PII_encoding[PII_id])
            password_input.append(sample['input'])
            batch_PII_input[i_batch]=PII_input
            batch_y[i_batch]=to_categorical(sample['output'],len(code))

        # batch_PII_input=sequence.pad_sequences(batch_PII_input,maxlen=PII_size,padding='post')
        batch_password_input=sequence.pad_sequences(password_input,maxlen=max_token_length,padding='post')
        print(batch_password_input)
        print(batch_PII_input)
        return [batch_PII_input,batch_password_input], batch_y
    def on_epoch_end(self):
        np.random.shuffle(self.samples)

def train_gen():
    return DataGenSequence('train')

def valid_gen():
    return DataGenSequence('valid')
