import chardet
with open("E:\\PII-Learning\\data\\clean_data.csv", 'rb') as rawdata:
    result = chardet.detect(rawdata.read(100000))
print(result)
import pandas as pd
data=pd.read_csv("E:\\PII-Learning\\data\\clean_data.csv",header=None)
import re
count=0
d=data.values
for i in range(537410):
    if d[i][0].lower() in str(d[i][7]).lower():
        reg = re.compile(re.escape(d[i][0]), re.IGNORECASE)
        temp=reg.sub('#', str(d[i][7]))
        d[i][7]=temp
for i in range(537410):
    l=str(d[i][3]).split('/')
    if len(l)>1:
        st=l[1]+l[2]
        if l[1] in d[i][7]:
            count+=1
            d[i][7]=d[i][7].replace(l[1], '~')
        elif l[2] in d[i][7]:
            count+=1
            d[i][7]=d[i][7].replace(l[2], '~')
for i in range(537410):
    l=str(d[i][2]).split(' ')
    if len(l)>1:
        if l[1] in str(d[i][7]):
            count+=1
            d[i][7]=str(d[i][7]).replace( l[1], '&')
        elif l[0] in str(d[i][7]):
             d[i][7]=str(d[i][7]).replace( l[0], '&')
for i in range(537410):
    l=str(d[i][1]).split('@')
    if l[0] in str(d[i][7]):
        count+=1
        d[i][7]=str(d[i][7]).replace( l[1], '&')
dat.to_csv('g://学习//replace.txt',sep='\t',index=0)