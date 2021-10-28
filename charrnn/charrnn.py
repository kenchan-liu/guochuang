import torch
from torch import nn
import torch.nn.functional as F
import numpy as np
import string
import random
import pandas as pd
device = torch.device("cuda")

chars = string.ascii_letters+'0123456789'+ ','+'.'+ '/'+'~'+ '!'+ '@'+ '#'+ '$'+ '%'+ '^'+ '&'+ '*'+ '('+')'+ '_'+ '+'+ '<'+'>'+ '?'+ ' '+ '{'+'}'+'|'+':'+'\"'+'['+']'+ '\\'+ '\''+';'+'`'+ '-'+'='+' '+'\n'

hidden_dim = 192
output_dim = len(chars)

#abc encode as [[1, ...], [0,1,...], [0,0,1...]]
def pw2input(name):
    ids = [chars.index(c) for c in name]
    a = np.zeros(shape=(len(ids), len(chars)), dtype=np.long)
    for i, idx in enumerate(ids):
        a[i][idx] = 1
    return a

# abc encode as [0 1 2]
def pw2target(name):
    ids = [chars.index(c) for c in name]
    return ids

def load():
    df =  pd.read_table('H:\\train.txt')
    data=df.as_matrix()
    data=data.reshape(-1)
    for i in range(len(data)):
        data[i]=" "+str(data[i])
    data=data.tolist()
    return data
class CharRNN(nn.Module):
    def __init__(self, vocab_size, hidden_size, output_size):
        super(CharRNN, self).__init__()
        self.vocab_size = vocab_size
        self.hidden_size = hidden_size
        self.output_size = output_size
        self.rnn = nn.GRU(vocab_size, hidden_size, batch_first=True)
        self.liner = nn.Linear(hidden_size, output_size)

    def forward(self,pw, hidden=None):
        if hidden is None:
            hidden = torch.zeros(1, 1, self.hidden_size, device=device) # 初始hidden state
        input = pw
        output, hidden = self.rnn(input, hidden)
        output = self.liner(output)
        output = F.dropout(output, 0.3)
        output = F.softmax(output, dim=2)
        return output.view(1, -1), hidden


class Model:
    def __init__(self, epoches):
        self.model = CharRNN(len(chars), hidden_dim , output_dim)
        self.model.to(device)
        self.epoches = epoches
    def save(self):
        torch.save(self.model.state_dict(), "h:\\t1.pth")
    def load(self,PATH):
        self.model.load_state_dict(torch.load(PATH))
        self.model.eval()
    def train(self, train_set):
        loss_func = nn.CrossEntropyLoss()
        optimizer = torch.optim.RMSprop(self.model.parameters(), lr=0.001)

        for epoch in range(self.epoches):
            total_loss = 0
            for x in range(10000):  # 每轮随机样本训练1000次
                loss = 0
                name = random.choice(train_set)
                optimizer.zero_grad()
                hidden = torch.zeros(1, 1, hidden_dim, device=device)
                for x, y in zip(list(name), list(name[1:]+'!')):
                    pw_tensor = torch.tensor([pw2input(x)], dtype=torch.float, device=device)
                    target_tensor = torch.tensor(pw2target(y), dtype=torch.long, device=device)
                    pred, hidden = self.model( pw_tensor, hidden)
                    loss += loss_func(pred, target_tensor)

                loss.backward()
                optimizer.step()

                total_loss += loss/(len(name) - 1)

            print("Training: in epoch {} loss {}".format(epoch, total_loss/1000))

    def sample(self, start):
        result = []
        with torch.no_grad():
            hidden = None
            """
            for c in start:
                pw_tensor = torch.tensor([pw2input(c)], dtype=torch.float, device=device)
                pred, hidden = self.model( pw_tensor, hidden)
            """
            c = start[-1]
            
            while c != '!':
                pw_tensor = torch.tensor([pw2input(c)], dtype=torch.float, device=device)
                pred, hidden = self.model( pw_tensor, hidden)
                topv, topi = pred.topk(1)
                print(topi,topv)
                c = chars[topi]
                result.append(c)


        return start + "".join(result[:-1])


if __name__ == "__main__":
    model = Model(50)
    data_set = load()
    
    model.train(data_set)
    model.save()
    c = input('start: ')
    while c != 'q':
        print(model.sample(c))
        print(model.sample(c))
        c = input('start: ')