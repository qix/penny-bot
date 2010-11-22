import sys, datetime


def analyze(log):
	bidders = {}
	try:
		for x in file(log):
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
					bidders[name] = clicks

					# onBid
					if name == 'qix' and lastClick:
						delay = time-lastClick[0]
						timeDelay = lastClick[1]-at
						if abs(timeDelay) < 1:
							delays.append(timeDelay)
							print timeDelay

				elif x[2] == 'next':
					at = float(x[4])
			except:
				print 'Fail on line:',x
	except:
		pass

	return {'bidders': bidders}



