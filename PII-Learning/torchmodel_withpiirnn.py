import tensorflow.keras.backend as K
import tensorflow as tf
from tensorflow.keras.layers import Input,Dense,LSTM,BatchNormalization, Concatenate,Embedding,RepeatVector,TimeDistributed,Dropout
from keras.models import Model
from tensorflow.keras.utils import plot_model
from pydot import *
from config import max_token_length
from config import vocab_size, embedding_size,PII_size

import torch
import random
from torch import nn
import torch.nn.functional as F
device = torch.device("cuda")

def build_model():
    #word embedding
    password_input = Input(shape=(max_token_length,),dtype='int32')
    x = Embedding(input_dim=vocab_size,output_dim=embedding_size)(password_input)
    x = LSTM(256, return_sequences=True)(x)
    x = BatchNormalization()(x)
    password_embedding = TimeDistributed(Dense(embedding_size))(x)

    # PII embedding
    PII_input =Input(shape=(PII_size,))
    x=Dense(embedding_size,activation='relu',name='PII_embedding')(PII_input)
    # the PII I is only input once
    PII_embedding =RepeatVector(1)(x)

    # language model
    x = [PII_embedding,password_embedding]
    x = Concatenate(axis=1)(x)
    x = Dropout(0.1)(x)
    x = LSTM(512,return_sequences=True,name='language_lstm_1')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.2)(x)
    x = LSTM(512,name='language_lstm_2')(x)
    x = BatchNormalization()(x)
    x = Dropout(0.4)(x)
    output = Dense(vocab_size,activation='softmax',name='output')(x)

    inputs=[PII_input,password_input]
    model = Model(inputs=inputs,outputs=output)
    return model
"""
torch model defined as below
"""
class PII_LSTM(nn.Module):
    def __init__(self,vocab_size,hidden_size1,hidden_size2,output_size):
        super(PII_LSTM, self).__init__()
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size1
        self.output_size = output_size
        self.embed = nn.embedding(vocab_size,embedding_size)
        self.piidense = nn.Linear(PII_size,embedding_size)
        self.dropout = nn.Dropout(0.2)
        self.layernorm = nn.BatchNorm1d()
        self.dropout2 = nn.Dropout(0.4)
        #self.linear = nn.Linear()
        self.rnn = nn.GRU(embedding_size, hidden_size1, batch_first=True)
        self.rnn2 = nn.GRU(embedding_size, 512, batch_first=True)
        self.rnn3 = nn.GRU(embedding_size, 512, batch_first=True)
        self.linear = nn.Linear(hidden_size1, output_size)

    def forward(self, pw,pii):

        hidden1 = torch.zeros(1, 1, 256, device=device)  # 初始hidden state
        hidden2 = torch.zeros(1, 1, 512, device=device)
        hidden3 = torch.zeros(1, 1, 512, device=device)
        input1 = pw
        input2 = pii
        pwem = self.embed(input1, embedding_size)
        out1 = self.rnn(pwem,hidden1)
        out1 = self.layernorm(out1)
        # what does repeatVector mean??
        # and how to use it in torch??
        output = nn.cat([out1,input2],dim=1)
        # concatenate the output and the input
        output = F.dropout(output, 0.1)
        output = self.rnn2(output,hidden2)
        output = self.dropout(output)
        output,hidden3 = self.rnn3(output,hidden3)
        output = F.dropout(output, 0.2)
        output = F.softmax(output, dim=2)
        return output.view(1, -1), hidden3
class Model:
    def __init__(self,epoches=10):
        self.model=PII_LSTM(len(__),256,512,len(__))  #input and output not yet decided
        self.model.to(device)
    def save(self):
        torch.save(self.model.state_dict(),".\\")
    def load(self,Path):
        self.model.load_state_dict(torch.load(Path))
        self.model.eval()
    def train(self,train_set):
        """
        
        :param train_set 
        you need to train this model
        transform your trainset as torch.tensor
        and train it for set epoches.
        """
        lossfunc = nn.categorical_crossentropy()
        optimizer = torch.optim.RMSprop(self.model.parameters(), lr=0.001)

        for epoch in range(self.epoches):
            total_loss = 0
            for x in range(10000):  # 每轮随机样本训练1000次
                loss = 0
                tr = random.choice(train_set)
                optimizer.zero_grad()
                for sel in tr:#you are suppose to divide the train data and the target
                    pw_tensor = torch.tensor(__, dtype=torch.float, device=device)
                    pii_tensor = torch.tensor(__, dtype=torch.float, device=device)
                    target_tensor = torch.tensor(__, dtype=torch.long, device=device)#replace it!
                    pred, hidden = self.model(pw_tensor, pii_tensor)
                    loss += lossfunc(pred, target_tensor)

                loss.backward()
                optimizer.step()

                total_loss += loss / (len(tr) - 1)

            #print("Training: in epoch {} loss {}".format(epoch, total_loss / 1000))
if __name__ == '__main__':
    with tf.device("/cpu:0"):
        model =  build_model()
    model.summary()
    # plot_model(model, to_file='model.svg', show_layer_names=True,show_shapes=True)

    K.clear_session()