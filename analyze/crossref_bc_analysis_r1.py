#!/usr/bin/env python3
# coding: utf-8
import json

infilenames_list = [
  'Current_Blockchain50051.json', 
  'Current_Blockchain50053.json',
  'Current_Blockchain50055.json',
  'Current_Blockchain50057.json',
  'Current_Blockchain50059.json',
  'Current_Blockchain50061.json',
  'Current_Blockchain50063.json',
  'Current_Blockchain50065.json'
  #'Current_Blockchain50089.json',
  #'Current_Blockchain50091.json'
]

count_dict = {}


for infilename in infilenames_list:
  signature_count = 0
  with open(infilename, 'r') as infile:
    for line in infile:
      data_list = json.loads(line)
      for data in data_list:
        if data['cross-ref'] != []:
          signature_count += 1
          block_hashes_list = data['cross-ref'].replace('[', '').replace('"', '').replace(' ', '').split(",")[:len(infilenames_list)]
          #print(infilename, block_hashes_list)
          #print(infilename, data)
          #print("---")
          for block_hash in block_hashes_list:
            if block_hash not in count_dict:
              count_dict[block_hash] = 1
            else:
              count_dict[block_hash] += 1
  print("---")
  print(infilename, signature_count)

print("-----")
sorted_count_dict = dict(sorted(count_dict.items(), key=lambda x:x[1], reverse=True))
success_count = 0
for k, v in sorted_count_dict.items():
  #print(k, v)
  if v==len(infilenames_list):
    success_count += 1
print("-----")
print("Success count:", success_count/len(infilenames_list))
print("Success rate:", success_count/len(sorted_count_dict))
