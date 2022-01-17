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
            if len(temp)>9: #invalid item
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
dir="F:\PII Research\Dataset\CiXiHR-PII"
dataFileName=dir+"\clean_data.csv"
output=dir+"\Recognize_data.csv"
replaceFileName=dir+"\Replace_word.csv"
# data=read_file(dataFileName)
# _,_,d=data.value
size=0
count=0
# d=data.values
PII_usage={'username':0,'email':0,'birth':0,'name':0,'sex':0,'postcode':0}
if __name__=="__main__":
    # file_detect(dataFileName)
    PIIs, passwords = read_file(dataFileName)
    size=len(PIIs)
    # print(PIIs)
    # print(passwords)
    replace_PII=[["Type","replace_PII"]]
    raw_password=["raw_password\n"]
    for i,PII in enumerate(PIIs):
        if i%100000==0:
            print('Recognize %d...\n'%i)
        #Username
        if PII[0].lower() in str(passwords[i]).lower():
            reg = re.compile(re.escape(PII[0]), re.IGNORECASE)
            temp=reg.sub('#', str(passwords[i]))
            PII_usage['username']+=1
            raw_password.append(passwords[i])
            replace_PII.append(['username',PII[0]])
            passwords[i]=temp

        #Birth
        birth=PII[3].split('/')
        if len(birth)>1:
            Y = int(birth[0])
            M = int(birth[1])
            D = int(birth[2])
            # print("birth: %s/%s/%s" % (Y, M, D))
            birthPattern=['%s%s%s'%(Y,M,D),'%s'%(Y),'%s%s'%(M,D),'%s%s'%(D,M),'%s%s%s'%(D,M,Y),'%s%s%s'%(M,D,Y),'%s%s'%(D,Y),'%s%s'%(Y,D),
                          '%s%s%s'%(Y%100,M,D),'%s'%(Y%100),'%s%s'%(M,D),'%s%s'%(D,M),'%s%s%s'%(D,M,Y%100),'%s%s%s'%(M,D,Y%100),'%s%s'%(D,Y%100),'%s%s'%(Y%100,D),
                          '%s%02d%02d'%(Y,M,D),'%02d%02d'%(M,D),'%02d%02d'%(D,M),'%02d%02d%s'%(D,M,Y),'%02d%02d%s'%(M,D,Y),'%02d%02d'%(Y,D),'%02d%02d'%(D,Y),
                          '%s%02d%02d'%(Y%100,M,D),'%02d%02d'%(M,D),'%02d%02d'%(D,M),'%02d%02d%s'%(D,M,Y%100),'%02d%02d%s'%(M,D,Y%100),'%02d%02d'%(Y%100,D),'%02d%02d'%(D,Y%100)]
            birthPattern.sort(key=lambda i: len(i), reverse=True)
            # print(birthPattern)
            for pattern in birthPattern:
                if pattern in passwords[i]:
                    PII_usage['birth']+=1
                    raw_password.append(passwords[i])
                    replace_PII.append(['birth', pattern])
                    passwords[i]=passwords[i].replace(pattern, '~')
        #Name
        l=str(PII[2]).split(' ')
        if len(l)>1:
            if l[1] in str(passwords[i]):
                PII_usage['name']+=1
                raw_password.append(passwords[i])
                replace_PII.append(['Name', PII[2]])
                passwords[i]=str(passwords[i]).replace(l[1], '&')
            if l[0] in str(passwords[i]):
                PII_usage['name'] += 1
                raw_password.append(passwords[i])
                replace_PII.append(['Name', PII[2]])
                passwords[i]=str(passwords[i]).replace(l[0], '&')

        #Email
        email=str(PII[1]).split('@')
        email_head=email[0]
        email_web=str(email[1]).split('.')[0]
        basic_pattern=re.compile(r'[a-zA-z]+|[0-9][0-9]+')
        email_indice=basic_pattern.findall(email_head)
        email_indice.append(email_web)
        # print(email_indice,PII[1])
        for indice in email_indice:
            if indice in str(passwords[i]):
                PII_usage['email']+=1
                raw_password.append(passwords[i])
                replace_PII.append(['Email', PII[1]])
                passwords[i]=str(passwords[i]).replace(indice, '&')

    totalMatch = sum([PII_usage[key] for key in PII_usage])
    print(PII_usage)
    print("Total Match: %d    MatchRate: %.2f%%"%(totalMatch,totalMatch/size*100))
    # write_file(output,PIIs,passwords)
    write_file(replaceFileName,replace_PII,raw_password)