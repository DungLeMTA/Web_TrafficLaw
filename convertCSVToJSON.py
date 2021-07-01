import csv
import json

file_object = open('o.csv', 'r',encoding="utf-8")
lines = csv.reader(file_object, delimiter=',', quotechar='"')
flag = 0
data=[]
for line in lines:
    data.append(line)
file_object.close()
file_json = open('Them1.json','w',encoding='utf-8')
i=1400
for line in data:
    str_ = ','.join(line)
    print(str_)
    str1 = str_.split(',', 1)
    file_json.writelines('{"index":{"_index" : "qaluat","_id":"'+str(i)+'"}}\n')
    str1[1] = str1[1].replace("\n"," ")
    file_json.writelines('{"question": "'+str1[0]+'", "answer": "'+str1[1]+'"}\n')
    i+=1
file_json.close()


