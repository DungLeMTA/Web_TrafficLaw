import csv
import random as rd

tiento = ['cho biết','cho tôi biết','cho tôi biết là','hãy cho biết','hãy cho tôi biết','hãy cho tôi biết là',
          'giải thích','hãy giải thích cho tôi','giải thích cho tôi biết là','hãy giải thích cho tôi biết là',
          'cho tôi biết rằng','hãy cho tôi biết rằng','giải thích cho tôi biết rằng','hãy giải thích cho tôi biết rằng',
          'cho tôi biết rằng là','giải thích cho tôi biết rằng là','hãy giải thích cho tôi rằng là']
#
# data =[]
# data_thaythe=[]
# sl = 0
# with open('/home/dung/PycharmProjects/Web_TrafficLaw/cau_hoi_luat_tuongtu.csv') as csv_file:
#     csv_reader = csv.DictReader(csv_file, delimiter=',')
#     line_count = 0
#     for row in csv_reader:
#         if str(row["label"]) == "1":
#             data.append(row["sentence1"])
#             line_count += 1
#             sl = line_count

# with open('/home/dung/PycharmProjects/Web_TrafficLaw/Tu_Dien_Thay_The.csv') as csv_file:
#     csv_reader = csv.DictReader(csv_file, delimiter=',')
#     line_count = 0
#     for row in csv_reader:
#         data_thaythe.append([])
#         for r in row:
#             b= ' '+str(r)+' '
#             data_thaythe[line_count].append(b)
#         line_count += 1

# print(data_thaythe)
# print(data)
#
# with open('/home/dung/PycharmProjects/Web_TrafficLaw/data_moi.csv','w') as csv_file:
#     line_count = 0
#     a=0
#     b=0
#     for row in data:
#         if row != []:
#             csv_file.writelines(str(row[0])+','+str(row[1]).lower().strip()+','+str(row[2]).lower().strip()+'\n')
#             for i in range(0,3):
#                 c = rd.randint(0,len(tiento)-1)
#                 csv_file.writelines(str(row[0])+ ',' + str(row[1]).lower().strip() + ',' + tiento[c]+ ' '+str(row[2]).lower().strip() + '\n')
# with open('/home/dung/PycharmProjects/Web_TrafficLaw/data_moi.csv','w') as csv_file:
#     for row in data:
#         if row != []:
#             csv_file.writelines(str(row[0])+','+str(row[1]).lower().strip()+','+str(row[2]).lower().strip()+'\n')
#             for i in range(0,3):
#                 c = rd.randint(0,len(tiento)-1)
#                 csv_file.writelines(str(row[0])+ ',' + str(row[1]).lower().strip() + ',' + tiento[c]+ ' '+str(row[2]).lower().strip() + '\n')

data1 = []

with open('/home/dung/PycharmProjects/Web_TrafficLaw/Data.csv') as csv_file:
    sl1 = 0
    sl0 = 0
    csv_reader = csv.DictReader(csv_file, delimiter=',')
    for row in csv_reader:
        if str(row["label"]) == "1":
            sl1 +=1
        else:
            sl0 += 1
    print('1: ',sl1)
    print('0: ',sl0)

#
# with open('/home/dung/PycharmProjects/Web_TrafficLaw/Data_0.csv','w') as csv_file:
#
#     for l in range(0,7000):
#         csv_file.writelines("0"+","+data1[rd.randint(0,len(data)-1)].lower().strip()+","+data[rd.randint(0,len(data)-1)].lower().strip()+'\n')







