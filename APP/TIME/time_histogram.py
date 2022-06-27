#!/usr/bin/env python3
import matplotlib.pyplot as plt

phase1_sec_list = []

infile = open("Phase1.txt", "r")
for line in infile:
  data_str = line.split(": ")[2].split(" ")[0]
  #print(data_str)
  phase1_sec_list.append(float(data_str))
#print(phase1_sec_list)

plt.hist(phase1_sec_list, bins=50, log=True)
plt.xlabel("phase1 latency time [cec.]")
plt.ylabel("frequency")
#plt.show()
plt.savefig("phase1-sec-hist.png")
plt.savefig("phase1-sec-hist.eps")
plt.clf()



phase2_sec_list = []

infile = open("Phase2.txt", "r")
for line in infile:
  data_str = line.split(": ")[2].split(" ")[0]
  #print(data_str)
  phase2_sec_list.append(float(data_str))
#print(phase1_sec_list)

ave = sum(phase2_sec_list) / len(phase2_sec_list)
print(ave)

plt.hist(phase2_sec_list, bins=200, log=False)
plt.xlabel("phase2 latency time [sec.]")
plt.ylabel("frequency")
#plt.show()
plt.savefig("phase2-sec-hist.png")
plt.savefig("phase2-sec-hist.eps")
plt.clf()





phase3_sec_list = []

infile = open("Phase3.txt", "r")
for line in infile:
  data_str = line.split(": ")[2].split(" ")[0]
  #print(data_str)
  phase3_sec_list.append(float(data_str))
#print(phase1_sec_list)

plt.hist(phase3_sec_list, bins=50, log=True)
plt.xlabel("phase3 latency time [sec.]")
plt.ylabel("frequency")
#plt.show()
plt.savefig("phase3-sec-hist.png")
plt.savefig("phase3-sec-hist.eps")
plt.clf()

