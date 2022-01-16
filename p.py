import chardet
import pandas as pd
import re


def file_detect(filename):
    with open(filename, 'rb') as rawdata:
        result = chardet.detect(rawdata.read(100000))
    print(result)

def read_file(filename):
    # data=pd.read_csv(filename,header=None)
    PIIs=[]
    passwords=[]
    with open(filename, "r") as f:
        for line in f.readlines():
            temp = line.split(',')
            if len(temp)>8: #invalid item
                continue
            else:
                PIIs.append(temp[:-1])
                passwords.append(temp[-1])
    return PIIs,passwords
def write_file(filename,PIIs,passwords):
    with open(filename, "w") as f:
        for i in range(len(PIIs)):
            string=""
            for item in PIIs[i]:
                string+=item+","
            string+=passwords[i]
            f.write(string)

dataFileName="F:\PII Research\Dataset\CiXiHR-PII\clean_data.csv"
output="F:\PII Research\Dataset\CiXiHR-PII\Recognize_data.csv"
data=read_file(dataFileName)
# _,_,d=data.value
count=0
# d=data.values

if __name__=="__main__":
    # file_detect(dataFileName)
    PIIs, passwords = read_file(dataFileName)
    # print(PIIs)
    # print(passwords)
    for i,PII in enumerate(PIIs):
        if PII[0].lower() in str(passwords[i]).lower():
            reg = re.compile(re.escape(PII[0]), re.IGNORECASE)
            temp=reg.sub('#', str(passwords[i]))
            passwords[i]=temp

        l=str(PII[3]).split('/')
        if len(l)>1:
            st=l[1]+l[2]
            if l[1] in passwords[i]:
                count+=1
                passwords[i]=passwords[i].replace(l[1], '~')
            elif l[2] in passwords[i]:
                count+=1
                passwords[i]=passwords[i].replace(l[2], '~')

        l=str(PII[2]).split(' ')
        if len(l)>1:
            if l[1] in str(passwords[i]):
                count+=1
                passwords[i]=str(passwords[i]).replace(l[1], '&')
            elif l[0] in str(passwords[i]):
                 passwords[i]=str(passwords[i]).replace(l[0], '&')

        l=str(PII[1]).split('@')
        if l[0] in str(passwords[i]):
            count+=1
            passwords[i]=str(passwords[i]).replace(l[1], '&')
    print(count)
    write_file(output,PIIs,passwords)