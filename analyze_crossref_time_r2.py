#!/usr/bin/env python3
# coding: utf-8
import json
import matplotlib.pyplot as plt
import sys
import re

import os
infilenames_list = []
for file in os.listdir():
    base, ext = os.path.splitext(file)
    if ext == '.json':
        infilenames_list.append(file)
        infilenames_list.sort()

"""
infilenames_list = [
  'Current_Blockchain50051.json', 
  'Current_Blockchain50053.json',
  'Current_Blockchain50055.json',
  'Current_Blockchain50057.json',
  'Current_Blockchain50059.json',
  'Current_Blockchain50061.json', 
  'Current_Blockchain50063.json',
  'Current_Blockchain50065.json',
  'Current_Blockchain50067.json',
  'Current_Blockchain50069.json',
  'Current_Blockchain50071.json', 
  'Current_Blockchain50073.json',
  'Current_Blockchain50075.json',
  'Current_Blockchain50077.json',
  'Current_Blockchain50079.json',
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
  'Current_Blockchain50109.json',
  'Current_Blockchain50111.json',
  'Current_Blockchain50113.json', 
  'Current_Blockchain50115.json',
  'Current_Blockchain50117.json',
  'Current_Blockchain50119.json',
  'Current_Blockchain50121.json',
  'Current_Blockchain50123.json', 
  'Current_Blockchain50125.json',
  'Current_Blockchain50127.json',
  'Current_Blockchain50129.json',
  'Current_Blockchain50131.json',
  'Current_Blockchain50133.json', 
  'Current_Blockchain50135.json',
  'Current_Blockchain50137.json',
  'Current_Blockchain50139.json',
  'Current_Blockchain50141.json',
  'Current_Blockchain50143.json', 
  'Current_Blockchain50145.json',
  'Current_Blockchain50147.json',
  'Current_Blockchain50149.json',
  'Current_Blockchain50151.json',
#  'Current_Blockchain50161.json', 
  'Current_Blockchain50163.json',
  'Current_Blockchain50165.json',
#  'Current_Blockchain50167.json',
  'Current_Blockchain50169.json',
  'Current_Blockchain50171.json', 
  'Current_Blockchain50173.json',
  'Current_Blockchain50175.json',
  'Current_Blockchain50177.json',
  'Current_Blockchain50179.json',
  'Current_Blockchain50181.json', 
  'Current_Blockchain50183.json',
  'Current_Blockchain50185.json',
  'Current_Blockchain50187.json',
  'Current_Blockchain50189.json',
#  'Current_Blockchain50191.json', 
  'Current_Blockchain50193.json',
  'Current_Blockchain50195.json',
  'Current_Blockchain50197.json',
  'Current_Blockchain50199.json',
  'Current_Blockchain50201.json', 
  'Current_Blockchain50203.json',
  'Current_Blockchain50205.json',
  'Current_Blockchain50209.json',
  'Current_Blockchain50211.json',
  'Current_Blockchain50213.json', 
  'Current_Blockchain50215.json',
#  'Current_Blockchain50217.json',
#  'Current_Blockchain50219.json',
#  'Current_Blockchain50221.json',
  'Current_Blockchain50223.json', 
  'Current_Blockchain50225.json',
  'Current_Blockchain50227.json',
  'Current_Blockchain50229.json',
  'Current_Blockchain50231.json',
  'Current_Blockchain50233.json', 
  'Current_Blockchain50235.json',
  'Current_Blockchain50237.json',
  'Current_Blockchain50239.json',
  'Current_Blockchain50241.json',
  'Current_Blockchain50243.json', 
  'Current_Blockchain50245.json',
  'Current_Blockchain50247.json',
  'Current_Blockchain50249.json',
  'Current_Blockchain50251.json'
]
"""

crossref_timestamps_dict = {}
crossref_blocknums_dict = {}


### main ###
for infilename in infilenames_list:
  with open(infilename, 'r') as infile:
    for line in infile:
      data_list = json.loads(line)
      for data in data_list:
        if data['cross-ref'] != []:
          match = re.search('^\[(.+?), \{\"previous_crossref_hash\"', data['cross-ref'])
          if match:
            sorted_match = str(sorted(match.group(1).split(', ')))
            #print(sorted_match); sys.exit(0)
            if sorted_match not in crossref_timestamps_dict:
              crossref_timestamps_dict[ sorted_match ] = (float(data['timestamp']))
            else:
              if type(crossref_timestamps_dict[ sorted_match ]) != tuple:
                tmp_list = [ crossref_timestamps_dict[ sorted_match ] ]
              else:
                tmp_list = list(crossref_timestamps_dict[ sorted_match ])
              tmp_list.append(float(data['timestamp']))
              crossref_timestamps_dict[ sorted_match ] = tuple(tmp_list)
  
            if sorted_match not in crossref_blocknums_dict:
              crossref_blocknums_dict[ sorted_match ] = (int(data['block_num']))
            else:
              if type(crossref_blocknums_dict[ sorted_match ]) != tuple:
                tmp_list = [ crossref_blocknums_dict[ sorted_match ] ]
              else:
                tmp_list = list(crossref_blocknums_dict[ sorted_match ])
              tmp_list.append(int(data['block_num']))
              crossref_blocknums_dict[ sorted_match ] = tuple(tmp_list)


crossref_number_of_nodes = []
for k, v in crossref_timestamps_dict.items():
#  print(k, v, len(v))
#  print(v, len(v))
  if type(v) == tuple:
    crossref_number_of_nodes.append(len(v))
#for k, v in crossref_blocknums_dict.items():
#  print(k, v, len(v))
#  print(v, len(v))

print('crossref # of nodes:', crossref_number_of_nodes, len(crossref_number_of_nodes))

#sys.exit(0)

crossref_delay_times_list = []
for k, v in crossref_timestamps_dict.items():
#  max_crossref_time = max(list(v)[1:])
#  min_crossref_time = min(list(v)[1:])
  if type(v) == tuple:
    max_crossref_time = max(list(v))
    min_crossref_time = min(list(v))
#  for item in list(v):
#    print(item - min_crossref_time)
    crossref_delay = max_crossref_time - min_crossref_time
    crossref_delay_times_list.append( crossref_delay )
print('crossref delay times:', crossref_delay_times_list)


#sys.exit(0)



crossref_delay_blocknums_list = []
for k, v in crossref_blocknums_dict.items():
#  max_crossref_time = max(list(v[1:]))
#  min_crossref_time = min(list(v[1:]))
  if type(v) == tuple:
    max_crossref_time = max(list(v))
    min_crossref_time = min(list(v))
#  for item in list(v):
#    print(item - min_crossref_time)
    crossref_delay = max_crossref_time - min_crossref_time
    crossref_delay_blocknums_list.append( crossref_delay )
print('crossref delay block_nums:', crossref_delay_blocknums_list)




### plot ###
plt.hist(crossref_delay_times_list, bins=100)
plt.xlabel('crossref delay time')
plt.ylabel('frequency')
#plt.show()
plt.savefig('histogram-delay_time.png')
plt.clf()

plt.hist(crossref_delay_blocknums_list, bins=100)
plt.xlabel('crossref delay block_num')
plt.ylabel('frequency')
#plt.show()
plt.savefig('histogram-delay_blocknum.png')
plt.clf()


