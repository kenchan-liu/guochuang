
import string

PII_size = 113
n_epochs=40
hidden_size=100
embedding_size=50
patience = 50
learning_rate=0.01
batch_size=200
num_train_samples=537072
num_valid_samples=537072
max_token_length=16
vocab_size=102
PII_path='data/'


start_word='<start>'
end_word='<end>'
all_characters = string.printable
n_characters = len(all_characters)
code = {}
decode={}
for index, letter in enumerate(all_characters):
    code[letter] = index
    decode[index]=letter
code[start_word] = n_characters
code[end_word] = n_characters + 1
decode[n_characters]=start_word
decode[n_characters+1]=end_word