import os,re,time,select,fcntl,datetime,random,sys,cgi,BaseHTTPServer,random
import chrome_remote_shell
from subprocess import PIPE,Popen

import smokoo, accurate, runner, sound
from analyze import analyze

import curses

cmd = {'-':[], 'f':[], '=':[], 'm':[], '0':[]}
items = []
modes = []
for x in sys.argv[1:]:
	if x[0] == '-' or x[0] == 'f' or x[0] == '=' or x[0] == 'm': cmd[x[0]].append(x[1:])
	elif x.isdigit(): items.append(x)
	else: modes.append(x)

############################
### CONFIGURATION
###########################

friendly = dict([(x,1) for x in ['usera', 'userb', 'userc']])

maxBids = None

firstBids = []

minimumBid = 0.11

snipeChance = 0.75
lateBid = None

defaultBid = (0.65, 0.3)
snipeBid = (0.15, 0.2)

selected = 0

for mode in modes:
	if mode == 'home': # Bid not from server
		minimumBid = 0.58
		snipeChance = 0.7
		defaultBid = (0.78, 0.2)
		snipeBid = (0.60, 0.05)
		lateBidLast = 0.7

	elif mode == 'safe-home':
		minimumBid = 0.88
		snipeChance = 0.7
		defaultBid = (1.48, 0.2)
		snipeBid = (1.0, 0.09)
		lateBidLast = 0.95

	elif mode == 'snipe-pro': # Aims right to the last 100ms, sometimes misses
		minimumBid = 0.10
		snipeChance = 0.7
		defaultBid = (0.18, 0.03)
		snipeBid = (0.11, 0.02)
		lateBidLast = 0.15

	elif mode == 'rare-snipe': # Mode used for over-night, snipes every so often but generally bids at just over 1 second
		minimumBid = 0.36
		firstBids = [minimumBid] * len(items)
		snipeChance = 0.13
		defaultBid = (1.24, 0.30)
		snipeBid = (0.61, 0.23)
		lateBidLast = 0.5

	elif mode == 'kill': # Adds a killing bid at +/- 4 seconds
		lateBid = (4, 1)
		lateBidChance = 0.4

	elif mode == 'human': # Over half the time act human and give a rather 300ms-800ms click
		snipeChance = 0.65
		defaultBid = (0.5, 0.2)

	elif mode == 'snipe': # Snipe all the time at around 300ms
		minimumBid = 0.28
		firstBids = []
		snipeChance = 0.7
		defaultBid = (0.33, 0.03)
		snipeBid = (0.29, 0.02)
		lateBidLast = 0.3

	elif mode == 'safe-snipe': # Snipe from 350-600ms
		minimumBid = 0.36
		firstBids = []
		snipeChance = 0.7
		defaultBid = (0.54, 0.03)
		snipeBid = (0.41, 0.03)
		lateBidLast = 0.4

	elif mode == 'normal':
		minimumBid = 0.17

		snipeChance = 0.2

		lateBid = (4, 1) # Late bid at / None
		lateBidChance = 0.4
		lateBidLast = 1.0

		defaultBid = (0.75, 0.2)
		snipeBid = (0.18, 0.1)
		lateBidLast = 0.3

		firstBids = [snipeBid]
	else:
		print 'Unknown mode:', mode
		sys.exit(1)

remoteShellPort = 9223
interface = 'eth0'

bidAdd = 0 # Amount of time to add on top of all bids (on top of minimum time)

###########################


if len(sys.argv) < 2:
	print 'Usage timer.py [item_id]'
	sys.exit(0)


screen = curses.initscr()
curses.start_color()
curses.curs_set(0)
screen.nodelay(1)

normal_color, my_bid_color, last_second_color, my_last_second_color, stats_color = range(1,6)
curses.init_pair(normal_color, curses.COLOR_WHITE, curses.COLOR_BLACK)
curses.init_pair(my_bid_color, curses.COLOR_CYAN, curses.COLOR_BLACK)
curses.init_pair(last_second_color, curses.COLOR_RED, curses.COLOR_BLACK)
curses.init_pair(my_last_second_color, curses.COLOR_GREEN, curses.COLOR_BLACK)
curses.init_pair(stats_color, curses.COLOR_YELLOW, curses.COLOR_BLACK)

for x in cmd['-']: friendly[x] = True
for x in cmd['f']: firstBids.insert(0, float(x))
for x in cmd['=']: maxBids = int(x)


global myBids

def calcBid(n):
	global minimumBid, bidAdd
	if type(n) == tuple: n = random.gauss(n[0], n[1])
	return max(minimumBid, n) + bidAdd

def nextBid(last):
	global myBids, snipeChance, snipeBid, defaultBid, firstBids, lateBid, lateBidChance, lateBidLast

	bidAt = None

	# First bid at ***
	try: bidAt = firstBids.pop(0)
	except: pass

	# 25% of the time go for a 5'ish second bid after a last second bid
	if lateBid and bidAt is None and last and last < lateBidLast and random.random() < lateBidChance:
		bidAt = lateBid

	# 80% of the time be risky
	if bidAt is None and random.random() < snipeChance: bidAt = snipeBid

	# Otherwise look normal'ish
	if bidAt is None: bidAt = defaultBid

	return calcBid(bidAt)

	


sounds = sound.sound()
site = smokoo.smokoo(interface=interface)
browser = runner.runner(remoteShellPort, 'smokoo.co.za')
browser.run('window.alert=alert=function(){};')


def log(item, m):
	logfile = file(str(item)+'.log','a')
	print >> logfile, datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S'), m
	logfile.close()

clicks = {}
lastBidder = {}
bidders = {}
myBids = {}
bidTime = {}
timing = {}

for x in items:
	timing[x] = accurate.accurate()
	lastBidder[x] = False
	bidders[x] = analyze(str(x)+'.log')['bidders']
	myBids[x] = 0
	clicks[x] = []
	bidTime[x] = nextBid(False)
	log(x, 'first at %.2f' % (bidTime[x]))

sounds.start()

lastRefresh = 0

frame = 0
try:
	while True:
		frame += 1
		doSleep = True
		try:
			ch = screen.getch()
			if ch == ord('1'): bidTime[items[0]] += 1
			elif ch == ord('2'): bidTime[items[1]] += 1
			elif ch == ord('3'): bidTime[items[2]] += 1
			elif ch == ord('n'): selected = (selected + 1) % len(items)
			elif ch == ord('+'): bidTime[items[selected]] += 0.05
			elif ch == ord('-'): bidTime[items[selected]] -= 0.05
			elif ch == ord('b'): bidTime[items[selected]] += 60
			elif ch == ord('f'):
				if lastBidder[items[selected]] in friendly: del friendly[lastBidder[items[selected]]]
				else: friendly[lastBidder[items[selected]]] = True

			#if screen.getch() == ord('q'):
			#break
		except:
			pass
		
		readings = site.latest()
		#for item,reading in readings:
		#if not reading: continue
		# log all readings here

		screen.clear()
		for line in range(len(items)):
			item = items[line]
			if not item: continue
			if item in readings:
				reading = readings[item]
			else:
				reading = None

			if type(reading) is str: # game over
				if not reading in bidders[item]: bidders[item][reading] = 0
				log(item, 'over "%s" @ %.2f = %d' % (reading, timing[item].current(), bidders[item][reading]))
				if reading in friendly:
					sounds.win()
				else:
					sounds.lose()
				# Remove this item and continue
				items[items.index(item)] = None
				continue

			if timing[item].check_frozen():
				if lastRefresh + 15 < time.time():
					for x in items:
						if x: log(x, 'refresh')
					lastRefresh = time.time()
					browser.refresh()

			if reading is not None:
				(reading, amount, bidder) = reading
				if lastBidder[item] is None:
					lastBidder[item] = bidder
				elif bidder != lastBidder[item]:
					if bidder in bidders[item]: bidders[item][bidder] += 1
					else: bidders[item][bidder] = 1

					if clicks[item] and bidder in friendly:
						log(item, 'delay %.2f' % (timing[item].current() - clicks[item][-1]))

					log(item,'bid "%s" @ %.2f = %d' % (bidder, timing[item].current(), bidders[item][bidder]))
					lastBidder[item] = bidder

				timing[item].reading(reading)

			output = item + ': ' + timing[item].summary()
			if lastBidder[item]: output += ' #'+lastBidder[item]
			output += ' @ %.2f' % bidTime[item]
			try: output += ' = %d' % bidders[item][lastBidder[item]]
			except: pass

			if items[selected] == item: output = '* '+output
			else: output = '  '+output

			current = timing[item].current()

			if current < 5:
				if lastBidder[item] in friendly: color = my_last_second_color
				else: color = last_second_color
			else:
				if lastBidder[item] in friendly: color = my_bid_color
				else: color = normal_color

			screen.insstr(line, 0, output, curses.color_pair(color))

			if current - 0.1 < bidTime[item]: doSleep = False

			if current < bidTime[item] and not lastBidder[item] in friendly:
				if maxBids is not None and sum(myBids.itervalues()) >= maxBids:
					pass
				elif site.bid(item, browser):
					time.sleep(0.2) # Free up a bit of pc power for the bid, not really needed but heh
					sounds.bid()
					myBids[item] += 1
					bidTime[item] = nextBid(bidTime[item])
					clicks[item].append(current)
					log(item,'click @ %.2f = %d' % (current, myBids[item]))
					log(item,'next @ %.2f' % (bidTime[item]))
					if maxBids is not None and sum(myBids.itervalues()) == maxBids:
						sounds.nobids()
						log(item,'last')


		if maxBids is None:
			screen.insstr(len(items), 0, 'Clicks: %d' % (sum(myBids.itervalues())), curses.color_pair(stats_color))
		else:
			screen.insstr(len(items), 0, 'Clicks %d of %d' % (sum(myBids.itervalues()), maxBids), curses.color_pair(stats_color))
		screen.insstr(len(items)+1, 0, '%s' % (', '.join(modes)), curses.color_pair(stats_color))
		if frame % 10 == 0: screen.refresh()
		if doSleep: time.sleep(0.1)
except Exception, e:
	curses.reset_shell_mode()
	raise
