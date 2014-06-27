import time
import re
import datetime
import sys

f = open(sys.argv[1],'r')
total = 0
count =0
for line in f:
	if "From" in line:
		minutes,seconds = line.split()[7].split(':')
		total += int(minutes) * 60 + int(seconds)
		count +=1
aver = total / count
print 'average = '+datetime.datetime.fromtimestamp(aver).strftime('%M:%S')


