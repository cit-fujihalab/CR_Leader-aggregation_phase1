#!/usr/bin/env python3
# coding: utf-8
import json
import matplotlib.pyplot as plt

import os
infilenames_list = []
for file in os.listdir():
    base, ext = os.path.splitext(file)
    if ext == '.json':
        infilenames_list.append(file)
        infilenames_list.sort()


"""
infilenames_list = [
  'Current_Blockchain50081.json', 
  'Current_Blockchain50083.json',
  'Current_Blockchain50085.json',
  'Current_Blockchain50087.json',
  'Current_Blockchain50089.json',
  'Current_Blockchain50091.json', 
  'Current_Blockchain50093.json',
  'Current_Blockchain50095.json',
  'Current_Blockchain50097.json',
  'Current_Blockchain50099.json',
  'Current_Blockchain50101.json', 
  'Current_Blockchain50103.json',
  'Current_Blockchain50105.json',
  'Current_Blockchain50107.json',
  'Current_Blockchain50109.json',
  'Current_Blockchain50111.json', 
  'Current_Blockchain50113.json',
#  'Current_Blockchain50115.json',
  'Current_Blockchain50117.json',
#  'Current_Blockchain50119.json',
#  'Current_Blockchain50121.json', 
#  'Current_Blockchain50123.json',
  'Current_Blockchain50125.json',
  'Current_Blockchain50127.json',
  'Current_Blockchain50129.json',
  'Current_Blockchain50131.json', 
  'Current_Blockchain50133.json',
#  'Current_Blockchain50135.json',
#  'Current_Blockchain50137.json',
#  'Current_Blockchain50139.json',
  'Current_Blockchain50141.json', 
  'Current_Blockchain50143.json',
  'Current_Blockchain50145.json',
  'Current_Blockchain50147.json',
  'Current_Blockchain50149.json',
  'Current_Blockchain50151.json', 
#  'Current_Blockchain50153.json',
  'Current_Blockchain50155.json',
  'Current_Blockchain50157.json',
  'Current_Blockchain50159.json',
  'Current_Blockchain50161.json', 
  'Current_Blockchain50163.json',
#  'Current_Blockchain50165.json',
  'Current_Blockchain50167.json',
  'Current_Blockchain50169.json',
#  'Current_Blockchain50171.json', 
  'Current_Blockchain50173.json',
  'Current_Blockchain50175.json',
  'Current_Blockchain50177.json',
  'Current_Blockchain50179.json',
#  'Current_Blockchain50181.json', 
  'Current_Blockchain50183.json',
#  'Current_Blockchain50185.json',
  'Current_Blockchain50187.json',
#  'Current_Blockchain50189.json',
  'Current_Blockchain50191.json', 
#  'Current_Blockchain50193.json',
#  'Current_Blockchain50195.json',
#  'Current_Blockchain50197.json',
  'Current_Blockchain50199.json',
  'Current_Blockchain50201.json', 
#  'Current_Blockchain50203.json',
#  'Current_Blockchain50205.json',
  'Current_Blockchain50207.json',
#  'Current_Blockchain50209.json',
  'Current_Blockchain50211.json', 
#  'Current_Blockchain50213.json',
#  'Current_Blockchain50215.json',
  'Current_Blockchain50217.json',
  'Current_Blockchain50219.json'
]

"""


crossref_timestamps_all_list = []
crossref_blocknums_all_list = []


### main ###
for infilename in infilenames_list:
  crossref_timestamps_list = []
  crossref_blocknum_list = []
  with open(infilename, 'r') as infile:
    for line in infile:
      data_list = json.loads(line)
      for data in data_list:
        if data['cross-ref'] != []:
          block_num = int(data['block_num'])
          timestamp = float(data['timestamp'])
          crossref_timestamps_list.append( timestamp )
          crossref_blocknum_list.append( block_num )
  crossref_timestamps_all_list.append( crossref_timestamps_list )
  crossref_blocknums_all_list.append( crossref_blocknum_list )
#print(crossref_timestamps_all_list)
#print(crossref_blocknums_all_list)

crossref_inter_timestamps_list = []
for i in range(len(crossref_timestamps_all_list)):
  prev_timestamp = crossref_timestamps_all_list[i][0]
  for j in range(1,len(crossref_timestamps_all_list[i])):
    timestamp = crossref_timestamps_all_list[i][j]
    inter_timestamp = timestamp - prev_timestamp
    crossref_inter_timestamps_list.append( inter_timestamp )
    prev_timestamp = timestamp
print('inter-timestamps:', crossref_inter_timestamps_list)

crossref_inter_blocknums_list = []
for i in range(len(crossref_blocknums_all_list)):
  prev_blocknum = crossref_blocknums_all_list[i][0]
  for j in range(1,len(crossref_blocknums_all_list[i])):
    blocknum = crossref_blocknums_all_list[i][j]
    inter_blocknum = blocknum - prev_blocknum
    crossref_inter_blocknums_list.append( inter_blocknum )
    prev_blocknum = blocknum
print('inter-blocknums:', crossref_inter_blocknums_list)

### plot ###
plt.hist(crossref_inter_timestamps_list, bins=100)
plt.xlabel('inter-timestamp')
plt.ylabel('frequency')
#plt.show()
plt.savefig('histogram-inter_timestamp.png')
plt.clf()

plt.hist(crossref_inter_blocknums_list, bins=100)
plt.xlabel('inter-block_num')
plt.ylabel('frequency')
#plt.show()
plt.savefig('histogram-inter_blocknum.png')
plt.clf()


