import sys, datetime
from math import sqrt

username = 'usera'

if len(sys.argv) < 2:
	print 'Usage timer.py [item_id]'
	sys.exit(0)

def stddev(numbers):
	mean = sum(numbers) / (len(numbers)+0.0)
	return sqrt(sum([(x-mean)**2 for x in numbers]) / float(len(numbers)-1))


lastClick = None
delays = []
for x in file(sys.argv[1]):
	try:
		if x.strip() == '': continue
		x = x.strip().split(' ')
		time = x[0].split('-') + x[1].split(':')
		time = datetime.datetime(*map(int,time))
		if x[2] == 'click':
			at,clicks = float(x[4]),int(x[6])

			# onClick
			lastClick = (time,at)
		elif x[2] == 'bid':
			name,at,clicks = x[3][1:-1],float(x[5]),int(x[7])

			# onBid
			if name == username and lastClick:
				delay = time-lastClick[0]
				timeDelay = lastClick[1]-at
				if abs(timeDelay) < 1:
					delays.append(timeDelay)
					print timeDelay

		elif x[2] == 'next':
			at = float(x[4])
	except:
		print 'Fail on line:',x


print "Average:", sum(delays)/(len(delays)+0.0)
print "Standard Deviation:", stddev(delays)


